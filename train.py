from dotenv import load_dotenv
load_dotenv()

import argparse
import os
import pandas as pd
import numpy as np
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import  StandardScaler, FunctionTransformer, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
 

if __name__ == "__main__":

    # Set your variables for your environment
    EXPERIMENT_NAME="fraud_detector"

    # Set tracking URI 
    mlflow.set_tracking_uri("http://localhost:4000/")

    ### MLFLOW Experiment setup
    # # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)
    # Get our experiment info
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    #client = mlflow.tracking.MlflowClient()
    #mlflow.set_tracking_uri(os.environ["APP_URI"])

    #run = client.create_run(experiment.experiment_id)

    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False) # We won't log models right away

    # Parse arguments given in shell script
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators", default=5)
    parser.add_argument("--min_samples_split", default=2)
    args = parser.parse_args()

    # Import dataset
    df = pd.read_csv("https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv", index_col=0)
    df = df.astype({col: "float64" for col in df.select_dtypes(include=["int"]).columns})

    # X, y split 
    X = df.iloc[:, 0:-1]
    y = df.iloc[:, -1]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    print(df.columns)

    # Preprocessing 
    def dataset_processing(df):
        df = df.copy()
        ## Create new features

        # Calculate distance between transaction location and merchant location
        df['distance'] = (((df['lat'] - df['merch_lat'])*np.cos(np.radians((df['long'] + df['merch_long'])/2)))**2 + (df['long'] - df['merch_long'])**2)**1/2*111.12

        # calculate age
        df['age'] = pd.to_numeric(2025 - pd.to_datetime(df['dob']).dt.year)

        # Extract day of week and month from transaction date
        df['trans_dayofweek'] = pd.to_datetime(df['trans_date_trans_time']).dt.day_name()
        df['trans_month'] = pd.to_datetime(df['trans_date_trans_time']).dt.month_name()

        ## Remove redundant info or non useful info
        df = df.drop(['trans_date_trans_time', 'unix_time','first', 'last', 'street', 'city','lat', 'long', 'job', 'dob', 'merchant', 'merch_lat', 'merch_long', 'trans_num'], axis=1)

        return df 

    date_preprocessor = FunctionTransformer(dataset_processing)

    # Preprocessing 
    X_train_after_dataset_processing = dataset_processing(X_train)
    categorical_features = X_train_after_dataset_processing.select_dtypes("object").columns # Select all the columns containing strings
    categorical_transformer = OneHotEncoder(drop='first', handle_unknown='error')

    numerical_feature_mask = ~X_train_after_dataset_processing.columns.isin(X_train_after_dataset_processing.select_dtypes("object").columns) # Select all the columns containing anything else than strings
    numerical_features = X_train_after_dataset_processing.columns[numerical_feature_mask]
    numerical_transformer = StandardScaler()

    feature_preprocessor = ColumnTransformer(
        transformers=[
            ("categorical_transformer", categorical_transformer, categorical_features),
            ("numerical_transformer", numerical_transformer, numerical_features)
        ]
    )

    # Pipeline 
    n_estimators = int(args.n_estimators)
    min_samples_split=int(args.min_samples_split)

    model = Pipeline(steps=[
        ("Dates_preprocessing", date_preprocessor),
        ('features_preprocessing', feature_preprocessor),
        ("Regressor",RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split))
    ])

    # Log experiment to MLFlow
    with mlflow.start_run(experiment_id = experiment.experiment_id) as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)

        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="fraud_detector",
            registered_model_name="fraud_detector_RF",
            signature=infer_signature(X_train, predictions)
        )
        
    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")