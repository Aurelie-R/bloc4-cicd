import os

import mlflow
import mlflow.sklearn
from dotenv import find_dotenv, load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

env_path = find_dotenv()
load_dotenv(env_path, override=True)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://0.0.0.0:4000")
MODEL_URI = os.getenv(
    "MLFLOW_MODEL_URI", "models:/fraud_detector_RF@production"
    
)


def load_mlflow_model(
    tracking_uri: str = MLFLOW_TRACKING_URI,
    model_uri: str = MODEL_URI,
):
    """
    Charge un modèle MLflow (sklearn) à partir d'un tracking URI et d'un model URI.
    Par défaut : modèle RF fraud_detector_RF.
    """
    logging.info(f"Chargement du modèle MLflow depuis {tracking_uri} avec le model URI {model_uri}...")
    mlflow.set_tracking_uri(tracking_uri)
    # logging.info("✅ Connexion au MLflow Tracking Server établie")
    model = mlflow.sklearn.load_model(model_uri)
    logging.info("✅ Model récupéré depuis MLflow")
    return model
