# monitoring/generate_reports.py
import schedule
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import evidently
from evidently import Report
from evidently.metrics import *
from evidently.presets import *

def load_recent_predictions(hours=24):
    """
    Charge les prédictions des dernières X heures depuis les logs
    
    Args:
        hours: Nombre d'heures à charger
        
    Returns:
        DataFrame avec features, predictions et targets (si disponibles)
    """
    if Path(__file__).parent == Path('/'):
        lib_dir = Path('/app/')
    else:
        lib_dir = Path(__file__).parent.parent
    predictions_file = Path(lib_dir,'data/monitoring_predictions.jsonl')
    
    if not predictions_file.exists():
        raise FileNotFoundError("Aucune prédiction loggée trouvée")
    
    # Charger toutes les prédictions
    predictions_list = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    with open(predictions_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            timestamp = datetime.fromisoformat(data['timestamp'])
            
            # Filtrer par date
            if timestamp >= cutoff_time:
                predictions_list.append(data)
    
    if not predictions_list:
        raise ValueError(f"Aucune prédiction trouvée dans les dernières {hours} heures")
    
    # Convertir en DataFrame
    all_features = []
    all_predictions = []
    all_actuals = []
    
    for pred in predictions_list:
        all_features.extend(pred['features'])
        all_predictions.extend(pred['predictions'])
        if pred['actuals']:
            all_actuals.extend(pred['actuals'])
    
    df = pd.DataFrame(all_features)
    df['prediction'] = all_predictions
    
    if all_actuals:
        df['target'] = all_actuals
    
    return df


def check_alerts(report):
    """
    Vérifie les métriques du rapport et envoie des alertes si nécessaire
    
    Args:
        report: Rapport Evidently généré
    """
    # Extraire les métriques du rapport
    report_dict = report.dict()
    alerts = []
    
    # Vérifier le data drift
    try:
        metrics = report_dict.get('metrics', [])
        for metric in metrics:
            metric_type = metric.get('metric_name', '')
            # Alerte sur data drift
            if 'DriftedColumnsCount' in metric_type:
                print("Vérification du DriftedColumnsCount")
                drift_share = metric.get('value', {}).get('share', 0)
                
                if drift_share > 0.3:  # Plus de 30% de features en drift
                    # alerts.append(f"⚠️ Data Drift détecté: {drift_share*100:.1f}% des features ont drifté")
                    alerts.append(f"Data Drift détecté: {drift_share*100:.1f}% des features ont drifté")
            
            if 'ValueDrift' in metric_type:
                print("Vérification du ValueDrift")
                column_name = metric.get('config', {}).get('column', 'Unknown Column')
                drift_value = metric.get('value', 0)
                threshold = metric.get('config', {}).get('threshold', 0)
        
                if drift_value > threshold:
                    # alerts.append(f"⚠️ Value Drift detected for column '{column_name}': Value ({drift_value:.3f}) > Threshold ({threshold:.3f})")
                    alerts.append(f"Value Drift detected for column '{column_name}': Value ({drift_value:.3f}) > Threshold ({threshold:.3f})")

            # Alerte sur performance
            if 'ClassificationQuality' in metric_type:
                print("Vérification du ClassificationQuality")
                result = metric.get('result', {})
                current_metrics = result.get('current', {})
                
                f1_score = current_metrics.get('f1', 0)
                precision = current_metrics.get('precision', 0)
                recall = current_metrics.get('recall', 0)
                
                if f1_score < 0.7:
                    # alerts.append(f"⚠️ F1-Score faible: {f1_score:.3f}")
                    alerts.append(f"F1-Score faible: {f1_score:.3f}")
                
                if recall < 0.75:  # Critique pour la détection de fraude
                    # alerts.append(f"🚨 ALERTE CRITIQUE: Recall trop faible ({recall:.3f}) - risque de fraudes non détectées")
                    alerts.append(f"ALERTE CRITIQUE: Recall trop faible ({recall:.3f}) - risque de fraudes non détectées")
    
    except Exception as e:
        # alerts.append(f"❌ Erreur lors de l'analyse des métriques: {str(e)}")
        alerts.append(f"Erreur lors de l'analyse des métriques: {str(e)}")
    
    # Envoyer les alertes
    if alerts:
        send_alerts(alerts)
        print(f"🔔 {len(alerts)} alerte(s) générée(s)")
    else:
        print("✅ Aucune alerte, tout est normal")


def send_alerts(alerts):
    """
    Envoie les alertes (email, Slack, logs, etc.)
    
    Args:
        alerts: Liste des messages d'alerte
    """
    if Path(__file__).parent == Path('/'):
        lib_dir = Path('/app/')
    else:
        lib_dir = Path(__file__).parent
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Logger dans un fichier
    alert_log_path = Path(lib_dir,'reports/alerts.log')
    alert_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(alert_log_path, 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Alertes - {timestamp}\n")
        f.write(f"{'='*60}\n")
        for alert in alerts:
            f.write(f"{alert}\n")
            print(alert)  # Afficher aussi en console
    
    # TODO: Intégrer avec votre système d'alertes
    # - Email via SMTP
    # - Slack webhook
    # - PagerDuty
    # - Etc.
    
    # Exemple pour Slack (à adapter avec votre webhook)
    # import requests
    # slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    # if slack_webhook:
    #     requests.post(slack_webhook, json={
    #         'text': f"🔔 Alertes Monitoring Fraude:\n" + "\n".join(alerts)
    #     })


def generate_daily_report():
    """Génère un rapport Evidently quotidien"""
    
    try:
        if Path(__file__).parent == Path('/'):
            lib_dir = Path('/app/')
        else:
            lib_dir = Path(__file__).parent
        print(f"🔄 Génération du rapport quotidien - {datetime.now()}")
        
        # Charger les données de référence
        reference_data = pd.read_parquet(Path(lib_dir,'reference_data/baseline.parquet'))
        print(f"✅ Données de référence chargées: {len(reference_data)} lignes")
        
        # Charger les prédictions des dernières 24h
        current_data = load_recent_predictions(hours=48)
        print(f"✅ Prédictions récentes chargées: {len(current_data)} lignes")
        # Générer le rapport
        report = Report(metrics=[
            # ClassificationPreset(),
            DataDriftPreset(),
        ])
        my_eval = report.run(reference_data=reference_data, 
                   current_data=current_data)
        print("✅ Rapport généré")
        # Sauvegarder
        report_dir = Path(lib_dir,'reports')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report_path = Path(report_dir, f'report_{timestamp}.html')
        my_eval.save_html(str(report_path))
        print(f"✅ Rapport sauvegardé: {report_path}")
        # Vérifier les alertes
        check_alerts(my_eval)
        
        print("✅ Rapport quotidien généré avec succès\n")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport: {str(e)}")
        # Logger l'erreur
        with open(Path(report_dir,'errors.log'), 'a') as f:
            f.write(f"{datetime.now()}: {str(e)}\n")


# Scheduler
schedule.every().day.at("02:00").do(generate_daily_report)

# Pour tester immédiatement (à commenter en production)
# schedule.every(5).minutes.do(generate_daily_report)

if __name__ == "__main__":
    print("🚀 Démarrage du service de monitoring Evidently")
    print("📊 Génération de rapports programmée à 02:00 chaque jour")
    print("⏳ En attente...\n")
    
    # Générer un rapport immédiatement au démarrage
    generate_daily_report()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
  