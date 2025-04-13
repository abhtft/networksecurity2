from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


## configuration of the Data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
import certifi

from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
            # Initialize MongoDB client
            print(f"Attempting to connect to MongoDB with URL: {MONGO_DB_URL}")
            self.client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=certifi.where())
            # Test the connection
            self.client.server_info()
            print(f"MongoDB connection established successfully")
            print(f"Available databases: {self.client.list_database_names()}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        """
        Read data from MongoDB or fall back to CSV
        """
        try:
            # First try MongoDB
            try:
                print(f"Attempting to read data from MongoDB collection: {self.data_ingestion_config.collection_name}")
                print(f"Database name: {self.data_ingestion_config.database_name}")
                
                # Get database and collection
                database = self.client[self.data_ingestion_config.database_name]
                collection = database[self.data_ingestion_config.collection_name]
                
                print("Fetching data from MongoDB...")
                df = pd.DataFrame(list(collection.find()))
                
                if "_id" in df.columns.to_list():
                    df = df.drop(columns=["_id"], axis=1)
                
                df.replace({"na": np.nan}, inplace=True)
                
                print(f"Successfully read data from MongoDB with {len(df)} rows")
                return df
                
            except Exception as mongo_error:
                print(f"MongoDB read failed: {str(mongo_error)}")
                print("Falling back to CSV file...")
                
                # Fall back to CSV
                file_path = "Network_Data/phisingData_L.csv"
                if not os.path.exists(file_path):
                    raise Exception(f"CSV file not found at {file_path}")
                    
                df = pd.read_csv(file_path)
                print(f"Successfully read data from CSV with {len(df)} rows")
                return df

        except Exception as e:
            print(f"Error in export_collection_as_dataframe: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            print(f"Saving data to feature store at: {feature_store_file_path}")
            
            #creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
            
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            print(f"Successfully saved {len(dataframe)} rows to feature store")
            return dataframe
            
        except Exception as e:
            print(f"Error in export_data_into_feature_store: {str(e)}")
            raise NetworkSecurityException(e, sys)
        
    def split_data_as_train_test(self,dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )
            
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info(f"Exported train and test file path.")

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
        
    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException
        