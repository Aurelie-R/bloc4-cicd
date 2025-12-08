# tests/test_transform.py

import pandas as pd
from app.transform import build_features_from_transaction, predict_fraud
from app.load_model import load_mlflow_model


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
    print("✅ build_features fonctionne.")