# tests/test_transform.py

import pandas as pd
from app.transform import build_features_from_transaction, predict_fraud
from app.load_model import load_mlflow_model
import logging


def test_build_features_from_transaction():
    """
    Test simple : vérifier que la fonction produit 1 ligne
    et contient la colonne trans_date_trans_time.
    """

    fake_transaction = {"columns":["cc_num","merchant","category","amt","first","last","gender","street","city","state","zip","lat","long","city_pop","job","dob","trans_num","merch_lat","merch_long","is_fraud","current_time"],
                        "index":[209900],
                        "data":[[180049032966888,"fraud_Ernser-Feest","home",89.5,"Michael","Flores","M","70761 Fitzpatrick Brooks Suite 631","Saxon","WI",54559,46.4959,-90.4383,795,"Television\film\video producer","1986-04-15","43bf3787d682a207fa59291c8a9c4614",46.904128,-90.911955,0,1765214590221]]}


    df = build_features_from_transaction(fake_transaction)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1, "❌ build_features doit produire 1 ligne"
    assert "trans_date_trans_time" in df.columns, "❌ la colonne 'adr' doit exister"
    assert "is_fraud" not in df.columns, "❌ la colonne 'is_fraud' doit être supprimée"
    logging.info("✅ build_features fonctionne.")



def test_predict_fraud_output_values():
    """
    Test simple :
    - fraud_pred doit être 0 ou 1
    - fraud_proba doit être entre 0 et 1
    """

    model = load_mlflow_model()

    # Fabriquer des features minimales valides
    features = pd.DataFrame(
        [
            {
                "cc_num": 180049032966888,
                "merchant" : "fraud_Ernser-Feest",
                "category" : "home",
                "amt" : 89.5,
                "first" : "Michael",
                "last" : "Flores",
                "gender" : "M",
                "street" : "70761 Fitzpatrick Brooks Suite 631",
                "city" : "Saxon",
                "state" : "WI",
                "zip" : 54559,
                "lat" : 46.4959,
                "long" : -90.4383,
                "city_pop" : 795,
                "job" : "Television\film\video producer",
                "dob" : "1986-04-15",
                "trans_num" : "43bf3787d682a207fa59291c8a9c4614",
                "merch_lat" : 46.904128,
                "merch_long" : -90.911955,
                "is_fraud" : 0,
                "unix_time": 1765214590.221,
                "trans_date_trans_time": "2024-09-08 14:03:10"
            }
        ]
    )

    pred_df = predict_fraud(model, features)

    pred = pred_df.loc[0, "fraud_pred"]
    proba = pred_df.loc[0, "fraud_proba"]

    assert pred in [0, 1], f"❌ fraud_pred doit être 0 ou 1, obtenu {pred}"
    assert 0 <= proba <= 1, f"❌ fraud_proba doit être entre 0 et 1, obtenu {proba}"

    print("✅ predict_fraud renvoie une classe valide + proba valide.")