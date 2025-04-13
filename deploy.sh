#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install required system dependencies
sudo apt-get install -y build-essential

# Create application directory
sudo mkdir -p /app/networksecurity
cd /app/networksecurity

# Install Python dependencies
sudo pip3 install -r requirements.txt

# Create necessary directories
sudo mkdir -p templates final_model prediction_output Network_Data data_schema Artifacts saved_models
sudo mkdir -p Artifacts/data_ingestion/feature_store
sudo mkdir -p Artifacts/data_ingestion/ingested
sudo mkdir -p Artifacts/data_validation/validated
sudo mkdir -p Artifacts/data_validation/invalid
sudo mkdir -p Artifacts/data_validation/drift_report
sudo mkdir -p Artifacts/data_transformation/transformed
sudo mkdir -p Artifacts/data_transformation/transformed_object
sudo mkdir -p Artifacts/model_trainer/trained_model

# Set permissions
sudo chmod -R 777 /app/networksecurity

# Create .env file with necessary environment variables
cat > .env << EOL
MONGO_DB_URL=mongodb://abhishek:0LiWdFRno2XWIGaP@cluster0-shard-00-00.yanlm.mongodb.net:27017,cluster0-shard-00-01.yanlm.mongodb.net:27017,cluster0-shard-00-02.yanlm.mongodb.net:27017/?ssl=true&replicaSet=atlas-nox15r-shard-0&authSource=admin&retryWrites=true&w=majority
MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}
MLFLOW_TRACKING_USERNAME=${MLFLOW_TRACKING_USERNAME}
MLFLOW_TRACKING_PASSWORD=${MLFLOW_TRACKING_PASSWORD}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_REGION=${AWS_REGION}
EOL

# Start the application using nohup to keep it running
nohup uvicorn app:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 & 