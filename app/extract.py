import os
import json
from datetime import datetime
import logging

import requests
import boto3
from dotenv import find_dotenv, load_dotenv

# Charger le .env
env_path = find_dotenv()
load_dotenv(env_path, override=True)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# === API URL ===
# API_URL = "https://sdacelo-real-time-fraud-detection.hf.space/current-transactions" # URL de l'école
API_URL = "https://aremusan-real-time-fraud-detection.hf.space/current-transactions" # URL personnelle

# === S3 ===
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
S3_BUCKET = os.getenv("BUCKET_NAME")
RAW_PREFIX = "data/raw"


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



def get_transaction() -> dict:
    """
    Appelle l'API Jedha pour récupérer une transaction.
    """
    url = API_URL
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    transaction_json = json.loads(r.text)
    transaction_json = json.loads(transaction_json)
    logging.info("✅ Transaction bancaire récupérée")
    return transaction_json

def save_transaction_to_s3(transaction_json: dict, timestamp: str) -> str:
    """
    Sauvegarde la transaction brute dans S3 au format JSON (layer raw/bronze).
    Retourne la clé S3 utilisée.
    """
    logging.info("Sauvegarde de la transaction brute dans S3...")
    
    # Convert data to JSON string
    json_data = json.dumps(transaction_json, ensure_ascii=False, indent=2)
    json_bytes = json_data.encode('utf-8')
    
    # Create a unique filename with timestamp
    raw_name = f"{timestamp}_transaction_data.json"
    raw_key = f"{RAW_PREFIX}/{raw_name}"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=raw_key,
        Body=json_bytes,
        ContentType='application/json',
        ContentEncoding='utf-8'
    )
    logging.info(f"✅ Raw transaction envoyée sur s3://{S3_BUCKET}/{raw_key}")
    


def extract_transaction() -> tuple[dict, str]:
    """
    Étape complète d'extraction :
    - appelle l'API de transactions bancaires
    - sauvegarde la transaction JSON en raw S3
    Retourne (transaction, timestamp).
    """
    transaction = get_transaction()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    save_transaction_to_s3(transaction, timestamp)
    return transaction, timestamp

