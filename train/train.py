from dotenv import load_dotenv
load_dotenv()

import argparse
import os
import pandas as pd
import numpy as np
import time
import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import  StandardScaler, FunctionTransformer, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from dotenv import find_dotenv, load_dotenv

env_path = find_dotenv()
load_dotenv(env_path, override=True)

# Set your variables for your environment
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://0.0.0.0:4000")
EXPERIMENT_NAME="fraud_detector"

# function for saving data reference for Evidently
def save_reference_data(X_test, y_test, predictions):
    reference = X_test.copy()
    reference["target"] = y_test
    reference["prediction"] = predictions
    reference.to_parquet("monitoring/reference_data/baseline.parquet")

if __name__ == "__main__":

    # Set tracking URI for MLFlow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    # mlflow.set_tracking_uri("http://localhost:4000")

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
    parser.add_argument("--n_estimators", default=3)
    parser.add_argument("--min_samples_split", default=5)
    args = parser.parse_args()

    # Import dataset
    df = pd.read_csv("https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv", index_col=0)
    df = df.astype({col: "float64" for col in df.select_dtypes(include=["int"]).columns})

    # X, y split 
    X = df.iloc[:, 0:-1]
    y = df.iloc[:, -1]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 42, stratify=y)

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
        # ("Regressor",RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split))
        ("Regressor",XGBClassifier(scale_pos_weight=len(y[y==0])/len(y[y==1])))
    ])

    # Create evaluation dataset
    eval_data = X_test
    eval_data["target"] = y_test

    # Log experiment to MLFlow
    with mlflow.start_run(experiment_id = experiment.experiment_id) as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)
        print("✅ Model trained")
        # Log model seperately to have more flexibility on setup 
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="fraud_detector",
            registered_model_name="fraud_detector_RF",
            signature=infer_signature(X_train, predictions)
        )
        print(f"✅ Model logged in MLflow with run_id {run.info.run_id}")

        # Evaluate model
        result = mlflow.models.evaluate(
            model=model_info.model_uri,
            data=eval_data,
            targets="target",
            model_type="classifier",
            evaluators=["default"],
        )
        print(f"Recall Score: {result.metrics['recall_score']:.3f}")
        print(f"F1 Score: {result.metrics['f1_score']:.3f}")
        print(f"ROC AUC: {result.metrics['roc_auc']:.3f}")

        # Save reference data for Evidently
        save_reference_data(X_test, y_test, model.predict(X_test))

        # Récupérer la dernière version du modèle
        client = MlflowClient()
        latest = client.get_latest_versions(
            "fraud_detector_RF", stages=["None"]
        )
        if latest:
            model_version = latest[-1].version
            print(f"[INFO] Model logged as version {model_version}")

            # Mettre à jour l’alias "candidate"
            client.set_registered_model_alias(
                name="fraud_detector_RF",
                alias="candidate",
                version=model_version,
            )
            print(f"[INFO] Alias 'candidate' now points to version {model_version}")
        else:
            print("[WARN] Aucun modèle trouvé dans le registre.")
        
    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")