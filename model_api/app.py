import mlflow 
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from fastapi import FastAPI, File
from fastapi.responses import HTMLResponse
import requests
import json
from datetime import datetime
from monitoring.evidently_monitor import log_prediction

API_URL = "https://aremusan-real-time-fraud-detection.hf.space/current-transactions" # URL personnelle
mlflow.set_tracking_uri('https://aremusan-mlflow.hf.space')

description = """
## Transation simulation
This endpoint calls an API to get a simulated CB transaction. Here is the endpoint:
* `/transaction` that returns a simulated transaction in JSON format.

## Machine Learning

This is a Machine Learning endpoint that predict salary given some years of experience. Here is the endpoint:

* `/predict` that accepts `floats`


Check out documentation below 👇 for more information on each endpoint. 
"""

tags_metadata = [
    {
        "name": "Transation simulation",
        "description": "Endpoint that call an API to get a simulated CB transaction."
    },
    {
        "name": "Machine Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="Fraud prediction API",
    description=description,
    version="0.1",
    contact={
        "name": "REMUSAN Aurelie",
    },
    openapi_tags=tags_metadata
)


class PredictionFeatures(BaseModel):
    trans_date_trans_time: str
    cc_num: float
    merchant: str
    category : str
    amt: float
    first: str
    last: str
    gender: str
    street: str
    city: str
    state: str
    zip: float
    lat: float
    long: float
    city_pop: float
    job: str
    dob: str
    trans_num: str
    unix_time: float
    merch_lat: float
    merch_long: float

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API de Transactions</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                .links {
                    margin-top: 20px;
                }
                .link-button {
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 10px 10px 10px 0;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }
                .link-button:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Bienvenue sur l'API de Transactions</h1>
                <p>Cette API permet de gérer et analyser les transactions.</p>
                <div class="links">
                    <a href="/docs" class="link-button">📚 Documentation (Swagger)</a>
                    <a href="/redoc" class="link-button">📖 Documentation (ReDoc)</a>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/transaction", tags=["Transation simulation"])
async def transaction():
    """
    Print informations about a CB transaction. 
    """
    url = API_URL
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    transaction_json = json.loads(r.text)
    transaction_json = json.loads(transaction_json)

    transaction_data = transaction_json["data"]
    columns = transaction_json["columns"]

    features = pd.DataFrame(transaction_data, columns=columns)
    features['unix_time'] = features['current_time']/1000
    features['trans_date_trans_time'] = pd.to_datetime(features['current_time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
    features.drop(columns=['current_time'], inplace=True)
    features = features.astype({col: "float64" for col in features.select_dtypes(include=["int"]).columns})
    features = features.drop(columns=['is_fraud'])

    transaction = features.to_dict(orient="records")[0]
    return transaction



@app.post("/predict", tags=["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction of fraud for a given CB transaction! (0 = not fraud, 1 = fraud) 
    """
    # Read data 
    transaction_to_test = pd.DataFrame(
        {
            "trans_date_trans_time": [predictionFeatures.trans_date_trans_time],
            "cc_num": [predictionFeatures.cc_num],
            "merchant": [predictionFeatures.merchant],
            "category": [predictionFeatures.category],
            "amt": [predictionFeatures.amt],
            "first": [predictionFeatures.first],
            "last": [predictionFeatures.last],
            "gender": [predictionFeatures.gender],
            "street": [predictionFeatures.street],
            "city": [predictionFeatures.city],
            "state": [predictionFeatures.state],
            "zip": [predictionFeatures.zip],
            "lat": [predictionFeatures.lat],
            "long": [predictionFeatures.long],
            "city_pop": [predictionFeatures.city_pop],
            "job": [predictionFeatures.job],
            "dob": [predictionFeatures.dob],
            "trans_num": [predictionFeatures.trans_num],
            "unix_time": [predictionFeatures.unix_time],
            "merch_lat": [predictionFeatures.merch_lat],
            "merch_long": [predictionFeatures.merch_long]
        }
    )

    # Log model from mlflow 
    logged_model = 'models:/fraud_detector_RF@production'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    #loaded_model = joblib.load('salary_predictor/model.joblib')

    prediction = loaded_model.predict(transaction_to_test)
    
    # # Log for evidently monitoring
    # log_prediction(
    #     features=transaction_to_test,
    #     prediction=prediction,
    #     timestamp=datetime.now()
    # )

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)