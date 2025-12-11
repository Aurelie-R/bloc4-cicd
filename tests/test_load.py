import random
from datetime import datetime
import logging
import pandas as pd
from sqlalchemy import create_engine, text

from app.load import (
    pg_connect,
    build_db_rows,
    ensure_predictions_table_exists,
    insert_predictions,
    DATABASE_URL,
)

def test_pg_connect():
    """
    Test très simple : la connexion doit s'établir sans erreur.
    """
    conn = pg_connect()
    assert conn is not None
    conn.close()
    logging.info("✅ Connexion à la base de données réussie.")


def test_ensure_predictions_table_exists():
    """
    Test très simple : la fonction ne doit pas lever d'erreur
    et la table doit exister après.
    """
    ensure_predictions_table_exists()

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'fraud_transaction_predictions';
                """
            )
        )
        table = result.fetchone()
        assert table is not None
        assert table[0] == "fraud_transaction_predictions"
        logging.info("✅ La table fraud_transaction_predictions existe en base.")





def test_build_db_rows_basic():
    """
    Teste que build_db_rows renvoie bien une liste de tuples
    avec les bonnes valeurs et la bonne longueur.
    """
    fake_prediction = random.randint(0, 1)
    fake_proba = random.uniform(0, 1)
    # Fake JSON minimal
    fake_transaction = {
        "columns":["cc_num","merchant","category","amt","first","last","gender","street","city","state","zip","lat","long","city_pop","job","dob","trans_num","merch_lat","merch_long","is_fraud","current_time"],
        "data":[[12345,"fraud_Test-merchant","home",89.5,"John","Doe","M","123 Southpark Ave","Saxon","WI",54559,46.4959,-90.4383,795,"Nothing","1986-04-15","43bf3787d682a207fa59291c8a9c4614",46.904128,-90.911955,0,1765214590221]]
    }

    # DataFrame de prédictions minimal
    pred_df = pd.DataFrame(
        [
            {
                "cc_num": "12345",
                "merchant" : "fraud_Test-merchant",
                "category" : "home",
                "amt" : 89.5,
                "first" : "John",
                "last" : "Doe",
                "gender" : "M",
                "street" : "123 Southpark Ave",
                "city" : "Saxon",
                "state" : "WI",
                "zip" : 54559,
                "lat" : 46.4959,
                "long" : -90.4383,
                "city_pop" : 795,
                "job" : "Nothing",
                "dob" : "1986-04-15",
                "trans_num" : "43bf3787d682a207fa59291c8a9c4614",
                "merch_lat" : 46.904128,
                "merch_long" : -90.911955,
                "unix_time": 1765214590.221,
                "trans_date_trans_time": "2024-09-08 14:03:10",
                "fraud_pred": fake_prediction,
                "fraud_proba": fake_proba
            }
        ]
    )

    rows = build_db_rows(
        transaction_json=fake_transaction,
        pred_df=pred_df
    )

    # On doit avoir exactement 1 ligne
    assert isinstance(rows, list)
    assert len(rows) == 1

    row = rows[0]
    # cc_num,trans_date_trans_time,merchant,category,amt,first_name,last_name,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,merch_lat,merch_long,unix_time,is_fraud,fraud_pred,fraud_proba,created_at
    assert row[0] == "12345"
    assert isinstance(row[1], datetime)
    assert row[2] == "fraud_Test-merchant"
    assert row[3] ==  "home"
    assert isinstance(row[4], float)
    assert row[5] ==  "John"
    assert row[6] ==  "Doe"
    assert row[7] ==  "M"
    assert isinstance(row[8], str)
    assert row[9] ==  "Saxon"
    assert row[10] ==  "WI"
    assert isinstance(row[11], str)
    assert isinstance(row[12], float)
    assert isinstance(row[13], float)
    assert isinstance(row[14], int)
    assert row[15] ==  "Nothing"
    assert row[16] ==  "1986-04-15"
    assert row[17] ==  "43bf3787d682a207fa59291c8a9c4614"
    assert isinstance(row[18], float)
    assert isinstance(row[19], float)
    assert isinstance(row[20], float)
    assert row[21] == 0
    assert row[22] == fake_prediction
    assert row[23] == fake_proba
    assert isinstance(row[24], datetime)
    logging.info("✅ build_db_rows renvoie bien la liste de tuples attendue.")


def test_insert_predictions_inserts_rows():
    """
    Test d'intégration simple :
    - on s'assure que la table existe
    - on insère une ligne "test"
    - on vérifie qu'elle est bien présente en base
    """
    ensure_predictions_table_exists()

    test_ccnum = str(datetime.now().timestamp()).replace(".", "")  # valeur unique

    # 1 seule ligne de test
    # cc_num,trans_date_trans_time,merchant,category,amt,first_name,last_name,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,merch_lat,merch_long,unix_time,is_fraud,fraud_pred,fraud_proba,created_at
    rows = [
        (
            test_ccnum,  # cc_num
            datetime.now(),  # trans_date_trans_time
            "Test Merchant",  # merchant
            "Test Category",  # category
            100.0,  # amt
            "Test",  # first_name
            "User",  # last_name
            "M",  # gender
            "123 Test St",  # street
            "Test City",  # city
            "TS",  # state
            "12345",  # zip
            40.7128,  # lat
            -74.0060,  # long
            100000,  # city_pop
            "Tester",  # job
            "1990-01-01",  # dob
            "TESTTRANS123",  # trans_num
            40.7130,  # merch_lat
            -74.0050,  # merch_long
            1700000000.0,  # unix_time
            0,  # is_fraud
            0,  # fraud_pred
            0.01,  # fraud_proba
            datetime.now(),  # created_at
        )
    ]

    insert_predictions(rows)

    # Vérification en base
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT COUNT(*) 
                FROM public.fraud_transaction_predictions
                WHERE cc_num = :ccnum
                """
            ),
            {"ccnum": test_ccnum},
        )
        count = result.scalar()
        assert count >= 1
        logging.info("✅ insert_predictions a inséré la ligne en base avec succès.")
