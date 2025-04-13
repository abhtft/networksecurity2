import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()

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


@app.get("/train")
async def train_route():
    try:
        #print("Starting training pipeline...")
        train_pipeline = TrainingPipeline()
        #print("Initialized training pipeline")
        train_pipeline.run_pipeline()
        #print("Training pipeline completed successfully")
        return Response("Training is successful")
    except Exception as e:
        error_msg = str(e)
        print(f"Error in training pipeline: {error_msg}")
        if isinstance(e, NetworkSecurityException):
            print(f"Stack trace: {e.error_message}")
        return {"error": f"Training failed: {error_msg}"}
    
@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Check if model files exist locally
        # if not os.path.exists("final_model/preprocessor.pkl") or not os.path.exists("final_model/model.pkl"):
        #     # Sync from S3
        #     s3_sync = S3Sync()
        #     aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model"
        #     s3_sync.sync_folder_from_s3(folder="final_model", aws_bucket_url=aws_bucket_url)
            
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

