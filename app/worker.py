import time
from run_pipeline import run_etl

if __name__ == "__main__":
    while True:
        try:
            run_etl()  # Lance une exécution unitaire de l'ETL
        except Exception as e:
            # Gestion des erreurs
            print(f"[ERROR] ETL failed: {e}")
        # attendre 5 secondes avant la prochaine requête
        time.sleep(5)