import os
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import find_dotenv, load_dotenv

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

env_path = find_dotenv()
load_dotenv(env_path, override=True)

DATABASE_URL = os.getenv("BACKEND_STORE_URI")


def pg_connect():
    return psycopg2.connect(DATABASE_URL)


def ensure_predictions_table_exists():
    """
    Crée la table fraud_transaction_predictions si elle n'existe pas.
    """
    engine = create_engine(DATABASE_URL)

    ddl_fraud_pred = """
    CREATE TABLE IF NOT EXISTS public.fraud_transaction_predictions (
        id SERIAL PRIMARY KEY,
        cc_num BIGINT,
        trans_date_trans_time TIMESTAMP,
        merchant VARCHAR,
        category VARCHAR,
        amt NUMERIC,
        first_name VARCHAR,
        last_name VARCHAR,
        gender VARCHAR,
        street VARCHAR,
        city VARCHAR,
        state VARCHAR,
        zip VARCHAR,
        lat NUMERIC,
        long NUMERIC,
        city_pop INTEGER,
        job VARCHAR,
        dob DATE,
        trans_num VARCHAR,
        merch_lat NUMERIC,
        merch_long NUMERIC,
        unix_time NUMERIC,
        is_fraud INTEGER,
        fraud_pred INTEGER,
        fraud_proba NUMERIC,
        created_at TIMESTAMP
    );
    """

    with engine.begin() as conn:
        conn.execute(text(ddl_fraud_pred))


def build_db_rows(
    transaction_json: dict,
    pred_df: pd.DataFrame
):
    """
    Construit une liste de tuples prêts à être insérés en base.
    """
    # Trouver l'index de la colonne 'is_fraud'
    index_is_fraud = transaction_json['columns'].index('is_fraud')
    # Récupérer la valeur
    is_fraud = transaction_json['data'][0][index_is_fraud]

    rows = []
    for _, row in pred_df.iterrows():
        rows.append(
            (
                int(row["cc_num"]),
                datetime.strptime(row["trans_date_trans_time"], "%Y-%m-%d %H:%M:%S"),
                str(row["merchant"]),
                str(row["category"]),
                float(row["amt"]),
                str(row["first"]),
                str(row["last"]),
                str(row["gender"]),
                str(row["street"]),
                str(row["city"]),
                str(row["state"]),
                str(row["zip"]),
                float(row["lat"]),
                float(row["long"]),
                int(row["city_pop"]),
                str(row["job"]),
                str(row["dob"]),
                str(row["trans_num"]),
                float(row["merch_lat"]),
                float(row["merch_long"]),
                float(row["unix_time"]),
                int(is_fraud),
                int(row["fraud_pred"]),
                float(row["fraud_proba"]),
                datetime.now(timezone.utc)
            )
        )
    # logging.info(f"✅ Construction des {len(rows)} lignes pour la DB terminée")
    return rows


def insert_predictions(rows):
    """
    Insère les lignes de prédiction dans la table fraud_transaction_predictions.
    """
    insert_sql = """
    INSERT INTO public.fraud_transaction_predictions
    (cc_num,trans_date_trans_time,merchant,category,amt,first_name,last_name,gender,street,city,state,zip,lat,long,
    city_pop,job,dob,trans_num,merch_lat,merch_long,unix_time,is_fraud,fraud_pred,fraud_proba,created_at)
    VALUES %s;
    """

    with pg_connect() as conn, conn.cursor() as cur:
        if rows:
            execute_values(cur, insert_sql, rows)
        conn.commit()
    logging.info(f"✅ Transaction écrite dans la database avec succès.")
