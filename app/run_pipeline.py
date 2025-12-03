from dotenv import find_dotenv, load_dotenv
import os
import boto3

from extract import extract_transaction
from load_model import load_mlflow_model
from transform import build_features_from_transaction, save_features_to_s3, predict_fraud, save_predictions_to_s3
from load import ensure_predictions_table_exists, build_db_rows, insert_predictions


import pandas as pd
import requests
import json
import mlflow
from sqlalchemy import create_engine
from datetime import datetime

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Charger le .env
env_path = find_dotenv()
load_dotenv(env_path, override=True)


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
S3_BUCKET = os.getenv("BUCKET_NAME")


boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def run_etl():
    """
    Pipeline permettant une seule exécution :
    Extract → Transform + Predict → Load.
    """
    logging.info("🔄 Début de boucle ETL")
    # Extract
    transaction_json, timestamp = extract_transaction()

    # Load model
    model = load_mlflow_model()

    # Transform + Predict
    features_df = build_features_from_transaction(transaction_json)
    save_features_to_s3(features_df, timestamp)

    pred_df = predict_fraud(model, features_df)
    save_predictions_to_s3(pred_df, timestamp)

    # Load → DB
    ensure_predictions_table_exists()
    rows = build_db_rows(
        transaction_json=transaction_json,
        pred_df=pred_df
    )
    insert_predictions(rows)

    

    








    # # Extract
    # offer_data, timestamp = extract_offer(
    #     hotel_id=HOTEL_ID,
    #     checkin_date=CHECKIN_DATE,
    #     checkout_date=CHECKOUT_DATE,
    # )

    # # Load model
    # model = load_mlflow_model()

    # # Transform
    # features_df = build_features_from_offer(offer_data)
    # save_cleaned_to_s3(features_df, timestamp)

    # pred_df = predict_cancellation(model, features_df)
    # save_predictions_to_s3(pred_df, timestamp)

    # # Load → DB
    # ensure_predictions_table_exists()
    # rows = build_db_rows(
    #     offer_json=offer_data,
    #     pred_df=pred_df,
    #     hotel_id=HOTEL_ID,
    #     checkin_date=CHECKIN_DATE,
    #     checkout_date=CHECKOUT_DATE,
    # )
    # insert_predictions(rows)


if __name__ == "__main__":
    run_etl()