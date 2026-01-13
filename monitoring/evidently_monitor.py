# monitoring/evidently_monitor.py
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union, Optional
import pandas as pd
import numpy as np

from dotenv import find_dotenv, load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

env_path = find_dotenv()
load_dotenv(env_path, override=True)


def log_prediction(
    features: Union[Dict, pd.DataFrame, List],
    prediction: Union[int, float, List, np.ndarray],
    actual: Optional[Union[int, float, List, np.ndarray]] = None,
    timestamp: Optional[datetime] = None,
    log_file: str = 'data/monitoring_predictions.jsonl'
):
    """
    Enregistre une prédiction pour le monitoring Evidently
    
    Args:
        features: Features utilisées pour la prédiction (dict, DataFrame ou list)
        prediction: Prédiction(s) du modèle
        actual: Valeur réelle (optionnel, si disponible)
        timestamp: Horodatage (par défaut: maintenant)
        log_file: Chemin du fichier de log
    """
    logging.info("📝 Logging de la prédiction pour le monitoring Evidently")
    if timestamp is None:
        timestamp = datetime.now()
    
    # Normaliser les features en liste de dictionnaires
    if isinstance(features, pd.DataFrame):
        features_list = features.to_dict('records')
    elif isinstance(features, dict):
        features_list = [features]
    elif isinstance(features, list):
        features_list = features
    else:
        raise ValueError(f"Type de features non supporté: {type(features)}")
    
    # Normaliser les prédictions en liste
    if isinstance(prediction, (int, float, np.integer, np.floating)):
        predictions_list = [prediction]
    elif isinstance(prediction, np.ndarray):
        predictions_list = prediction.tolist()
    elif isinstance(prediction, list):
        predictions_list = prediction
    else:
        predictions_list = [prediction]
    
    # Normaliser les actuals en liste (si fournis)
    actuals_list = None
    if actual is not None:
        if isinstance(actual, (int, float, np.integer, np.floating)):
            actuals_list = [actual]
        elif isinstance(actual, np.ndarray):
            actuals_list = actual.tolist()
        elif isinstance(actual, list):
            actuals_list = actual
        else:
            actuals_list = [actual]
    
    # Créer l'objet à logger
    logging.info("📝 Préparation de l'entrée de log")
    log_entry = {
        'timestamp': timestamp.isoformat(),
        'predictions': predictions_list,
        'features': features_list,
        'actuals': actuals_list
    }
    logging.info(f"📝 Entrée de log préparée : pred={predictions_list}, features={features_list}")
    
    # Obtenir le répertoire parent de la base de la librairie
    lib_dir = Path(__file__).parent.parent
    
    # Construire le chemin complet du fichier de log
    log_path = lib_dir / log_file
    
    # Créer le répertoire parent si nécessaire
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Écrire dans le fichier JSONL (une ligne par prédiction)
    try:
        logging.info(f"📝 Écriture de la prédiction dans le fichier {log_path}")
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"⚠️ Erreur lors du logging de la prédiction: {e}")


def log_batch_predictions(
    features_df: pd.DataFrame,
    predictions: Union[List, np.ndarray],
    actuals: Optional[Union[List, np.ndarray]] = None,
    timestamp: Optional[datetime] = None,
    log_file: str = '/data/monitoring_predictions.jsonl'
):
    """
    Enregistre un batch de prédictions pour le monitoring
    
    Args:
        features_df: DataFrame contenant les features
        predictions: Array/liste des prédictions
        actuals: Array/liste des valeurs réelles (optionnel)
        timestamp: Horodatage (par défaut: maintenant)
        log_file: Chemin du fichier de log
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Convertir en listes si nécessaire
    if isinstance(predictions, np.ndarray):
        predictions = predictions.tolist()
    
    if actuals is not None and isinstance(actuals, np.ndarray):
        actuals = actuals.tolist()
    
    # Logger
    log_prediction(
        features=features_df,
        prediction=predictions,
        actual=actuals,
        timestamp=timestamp,
        log_file=log_file
    )


def get_logged_predictions(
    hours: int = 24,
    log_file: str = '/data/monitoring_predictions.jsonl'
) -> pd.DataFrame:
    """
    Récupère les prédictions loggées des dernières X heures
    
    Args:
        hours: Nombre d'heures à récupérer
        log_file: Chemin du fichier de log
        
    Returns:
        DataFrame avec toutes les prédictions
    """
    log_path = Path(log_file)
    
    if not log_path.exists():
        return pd.DataFrame()
    
    from datetime import timedelta
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    predictions_list = []
    
    with open(log_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                timestamp = datetime.fromisoformat(data['timestamp'])
                
                if timestamp >= cutoff_time:
                    predictions_list.append(data)
            except Exception:
                continue
    
    if not predictions_list:
        return pd.DataFrame()
    
    # Convertir en DataFrame
    all_features = []
    all_predictions = []
    all_actuals = []
    
    for pred in predictions_list:
        all_features.extend(pred['features'])
        all_predictions.extend(pred['predictions'])
        if pred.get('actuals'):
            all_actuals.extend(pred['actuals'])
    
    df = pd.DataFrame(all_features)
    df['prediction'] = all_predictions
    
    if all_actuals:
        df['target'] = all_actuals
    
    return df