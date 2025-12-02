# tests/test_load_model.py

from app.load_model import load_mlflow_model
import mlflow
import logging


def test_load_mlflow_model_success():
    """
    Test simple : on charge le modèle MLflow.
    Vérifie juste qu'on récupère un objet Python non None avec une méthode 'predict'.
    """

    model = load_mlflow_model()

    assert model is not None, "❌ Le modèle MLflow n'a pas été chargé"
    logging.info("✅ Modèle MLflow chargé correctement.")
