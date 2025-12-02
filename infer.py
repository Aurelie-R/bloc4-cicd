from dotenv import load_dotenv
load_dotenv()


import pandas as pd
import requests
import json
import mlflow
from sqlalchemy import create_engine
import os
 

if __name__ == "__main__":

    # Set tracking URI 
    mlflow.set_tracking_uri("http://localhost:4000/")

    # Set model informations
    logged_model = 'runs:/bf781e6a105445afa07d064f8f1f30a3/fraud_detector'
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # Set database connection string
    # Connection string pour Neon
    connection_string = os.getenv("BACKEND_STORE_URI")
    engine = create_engine(connection_string)

    while True:
        print("================================")
        # print(f"Processing transaction {i+1}")

        print("calling API to generate transaction...")
        
        # Call external API to get a transaction
        r = requests.get("https://sdacelo-real-time-fraud-detection.hf.space/current-transactions")

        if r.status_code == 200:
            # Double parsing car l'API encode 2 fois
            donnees = json.loads(r.text)
            donnees = json.loads(donnees)

            donnees_transaction = donnees['data']
            columns = donnees['columns']  

            # Prepare data to stick input formtat of model 

            df = pd.DataFrame(donnees_transaction, columns=columns)
            df['unix_time'] = df['current_time']/1000
            df['trans_date_trans_time'] = pd.to_datetime(df['current_time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
            df.drop(columns=['current_time'], inplace=True)
            df = df.astype({col: "float64" for col in df.select_dtypes(include=["int"]).columns})
            data = df.drop(columns=['is_fraud'])

            print("making prediction...")

            # Predict on a Pandas DataFrame.
            prediction = loaded_model.predict(pd.DataFrame(data))

            print(f"Prediction for transaction: {prediction[0]}")

            if (prediction[0] == 1):
                print("************ Fraud detected! *************")

            # Add prediction to DataFrame
            df['prediction'] = prediction

            # Save transaction with prediction to database
            print("saving transaction to database...")

            # Écrire tout le DataFrame
            df.to_sql('transactions', engine, if_exists='append', index=False)
            wait_time = 10
        else :
            print(f"An error {r.status_code} occurred:", r.reason)
            wait_time = 60
    
        print(f"waiting for {wait_time} seconds before next transaction...\n")
        import time
        time.sleep(wait_time)
    print("ending...")



        