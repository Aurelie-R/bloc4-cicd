import os
from datetime import datetime

import pandas as pd
import boto3
from dotenv import find_dotenv, load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# from load_model import load_mlflow_model  # optionnel si tu veux l'utiliser ici

env_path = find_dotenv()
load_dotenv(env_path, override=True)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
S3_BUCKET = os.getenv("BUCKET_NAME")
SILVER_PREFIX = os.getenv("SILVER_PREFIX", "data/silver")
GOLD_PREFIX = os.getenv("GOLD_PREFIX", "data/gold")

boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def build_features_from_transaction(transaction_json: dict) -> pd.DataFrame:
    """
    Transforme la réponse API en un DataFrame prêt pour le modèle.
    """
    transaction_data = transaction_json["data"]
    columns = transaction_json["columns"]

    features = pd.DataFrame(transaction_data, columns=columns)
    features['unix_time'] = features['current_time']/1000
    features['trans_date_trans_time'] = pd.to_datetime(features['current_time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
    features.drop(columns=['current_time'], inplace=True)
    features = features.astype({col: "float64" for col in features.select_dtypes(include=["int"]).columns})
    features = features.drop(columns=['is_fraud'])

    return features


def save_features_to_s3(features_df: pd.DataFrame, timestamp: str) -> str:
    """
    Sauvegarde le DataFrame cleaned (features) en CSV dans S3 /silver.
    """
    # Convert data to CSV string
    csv_data = features_df.to_csv(index=False)
    
    # Create a unique filename with timestamp
    silver_name = f"{timestamp}_transaction_data_cleaned.csv"
    silver_key = f"{SILVER_PREFIX}/{silver_name}"

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=silver_key,
            Body=csv_data,
            ContentType='application/csv'
        )
        logging.info(f"✅ Silver transaction envoyée sur s3://{S3_BUCKET}/{silver_key}")
        return silver_key
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi sur S3 : {e}")
        raise e



def predict_fraud(model, features: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le modèle sur les features et renvoie un DataFrame avec les prédictions.
    """
    preds = model.predict(features)
    proba = model.predict_proba(features)

    result = features.copy()
    result["fraud_pred"] = preds
    result["fraud_proba"] = proba[:, 1]  # proba de la classe "fraude" (1)

    return result


def save_predictions_to_s3(pred_df: pd.DataFrame, timestamp: str) -> str:
    """
    Sauvegarde le DataFrame de prédictions en CSV dans S3 /gold.
    """
    # Convert data to CSV string
    csv_data = pred_df.to_csv(index=False)
    
    # Create a unique filename with timestamp
    gold_name = f"{timestamp}_transaction_data_cleaned.csv"
    gold_key = f"{GOLD_PREFIX}/{gold_name}"

    try : 
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=gold_key,
            Body=csv_data,
            ContentType='application/csv'
        )
        logging.info(f"✅ Gold transaction envoyée sur s3://{S3_BUCKET}/{gold_key}")
        return gold_key
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi sur S3 : {e}")
        raise e

