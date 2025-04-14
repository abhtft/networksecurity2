import os
import sys

from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

import mlflow
from urllib.parse import urlparse
import dagshub

import os
import dagshub

# Initialize DAGsHub only if ENABLE_DAGSHUB is set to True
DAGSHUB_TOKEN = os.getenv("DAGSHUB_TOKEN", "false").lower() == "true"

if DAGSHUB_TOKEN:
    dagshub.init(repo_owner='abh.tft', repo_name='networksecurity', mlflow=True)
    logging.info("DAGsHub integration initialized.")
else:
    logging.info("DAGsHub integration is disabled.")
# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
MLFLOW_TRACKING_USERNAME = os.getenv("MLFLOW_TRACKING_USERNAME")
MLFLOW_TRACKING_PASSWORD = os.getenv("MLFLOW_TRACKING_PASSWORD")

if MLFLOW_TRACKING_URI:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    if MLFLOW_TRACKING_USERNAME and MLFLOW_TRACKING_PASSWORD:
        os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
        os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
            # Set MLflow experiment
            mlflow.set_experiment("NetworkSecurity_Classification")
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self, best_model, classification_metric, model_name, params=None):
        try:
            with mlflow.start_run():
                # Log parameters
                if params:
                    mlflow.log_params(params)
                
                # Log metrics
                mlflow.log_metrics({
                    "f1_score": classification_metric.f1_score,
                    "precision_score": classification_metric.precision_score,
                    "recall_score": classification_metric.recall_score
                })
                
                # Log model
                mlflow.sklearn.log_model(
                    best_model,
                    f"{model_name}_model",
                    registered_model_name=f"NetworkSecurity_{model_name}"
                )
                
                # Log model type
                mlflow.log_param("model_type", model_name)
                
                logging.info(f"Successfully logged model {model_name} to MLflow")
        except Exception as e:
            logging.error(f"Error in MLflow tracking: {str(e)}")
            return

    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
            },
            "Random Forest":{
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                'learning_rate':[.1,.01,.001],
                'subsample':[0.6,0.9],
                'n_estimators': [8,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,128,256]
            }
        }
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                          models=models,param=params)
        
        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))

        ## To get best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        y_train_pred=best_model.predict(X_train)

        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        
        ## Track the experiments with mlflow
        self.track_mlflow(best_model, classification_train_metric, best_model_name, params.get(best_model_name, {}))

        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        self.track_mlflow(best_model, classification_test_metric, f"{best_model_name}_test", params.get(best_model_name, {}))

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=NetworkModel)
        #model pusher
        save_object("final_model/model.pkl",best_model)
        

        ## Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact


        


       
    
    
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
