
import os
import requests
from app.extract import get_transaction
from dotenv import find_dotenv, load_dotenv
import logging

env_path = find_dotenv()
load_dotenv(env_path, override=True)

def test_call_transaction_api():
    """
    Teste l'appel à l'API Jedha pour récupérer une transaction.
    On vérifie que :
    - le code de statut est 200.
    - le contenu est au format JSON.
    - le JSON contient 'data'
    - la réponse contient les champs attendus.
    """
    # --- 1) Vérification du status_code (appel direct) ---
    test_url = "https://sdacelo-real-time-fraud-detection.hf.space/current-transactions"
    r = requests.get(test_url, timeout=60)
    assert r.status_code == 200, f"❌ Échec de l'appel API, status code: {r.status_code}, attendu 200"

    # --- 2) Vérification du code get_transaction ---
    transaction = get_transaction()
    assert isinstance(transaction, dict), "❌ La transaction doit être un dictionnaire"
    assert "data" in transaction, "❌ La transaction doit contenir la clé 'data'"
    assert len(transaction["data"]) > 0, "❌ La transaction 'data' ne doit pas être vide"

    logging.info("✅ Test de l'appel API transaction réussi : statut 200 + format JSON correct + champs attendus présents et non vides.")

    