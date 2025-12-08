import time
from run_pipeline import run_etl
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    # while True:
    for i in range(30) : # Limiter à 30 itérations pour les tests
        try:
            logging.info("🚀 Démarrage du pipeline ETL")
            run_etl()  # Lance une exécution unitaire de l'ETL
        except Exception as e:
            # Gestion des erreurs
            print(f"[ERROR] ETL failed: {e}")
        # attendre 5 secondes avant la prochaine requête
        time.sleep(5)