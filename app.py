import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()

# Default MongoDB URL if environment variable is not set
default_mongo_url = 'mongodb://abhishek:0LiWdFRno2XWIGaP@cluster0-shard-00-00.yanlm.mongodb.net:27017,cluster0-shard-00-01.yanlm.mongodb.net:27017,cluster0-shard-00-02.yanlm.mongodb.net:27017/?ssl=true&replicaSet=atlas-nox15r-shard-0&authSource=admin&retryWrites=true&w=majority'

# Try different environment variable names and fallback to default
mongo_db_url = os.getenv("MONGO_DB_URL") or os.getenv("MONGODB_URL_KEY") or default_mongo_url
print("MongoDB URL being used:", mongo_db_url)

import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

# Initialize MongoDB client with retry logic
max_retries = 3
retry_count = 0
client = None

while retry_count < max_retries:
    try:
        print(f"Attempting MongoDB connection (attempt {retry_count + 1}/{max_retries})")
        client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.server_info()
        print("MongoDB Connected successfully!")
        break
    except Exception as e:
        print(f"MongoDB Connection Error (attempt {retry_count + 1}): {str(e)}")
        retry_count += 1
        if retry_count == max_retries:
            print("Failed to connect to MongoDB after all retries")
            # Continue without MongoDB for now
            client = None
            break

# Only setup database and collection if MongoDB is connected
if client:
    try:
        from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
        from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME
        database = client[DATA_INGESTION_DATABASE_NAME]
        collection = database[DATA_INGESTION_COLLECTION_NAME]
    except Exception as e:
        print(f"Error setting up MongoDB database/collection: {str(e)}")
        client = None

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mongodb_connected": client is not None}

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Check if model files exist locally
        if not os.path.exists("final_model/preprocessor.pkl") or not os.path.exists("final_model/model.pkl"):
            # Sync from S3
            s3_sync = S3Sync()
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model"
            s3_sync.sync_folder_from_s3(folder="final_model", aws_bucket_url=aws_bucket_url)
            
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in prediction: {error_msg}")
        return {"error": f"Prediction failed: {error_msg}"}

if __name__=="__main__":
    app_run(app, host="0.0.0.0", port=8000)
    app_run(app, host="0.0.0.0", port=8080)

