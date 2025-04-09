# Description: This script demonstrates how to connect to MongoDB using Python and insert a document into a collection.
import pymongo
import numpy as np
from datetime import datetime

# Define feature names based on your data
feature_names = [
    "having_IP_Address", "URL_Length", "Shortining_Service", "having_At_Symbol",
    "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain", "SSLfinal_State",
    "Domain_registeration_length", "Favicon", "port", "HTTPS_token", "Request_URL",
    "URL_of_Anchor", "Links_in_tags", "SFH", "Submitting_to_email", "Abnormal_URL",
    "Redirect", "on_mouseover", "RightClick", "popUpWindow", "Iframe", "age_of_domain",
    "DNSRecord", "web_traffic", "Page_Rank", "Google_Index", "Links_pointing_to_page",
    "Statistical_report", "Result"
]

# Your feature vector
feature_vector = [-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 1, -1, 
                  1, 1, 1, 0, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 0, 1, 1, 1, -1, -1, 
                  -1, 1, 1, 1, 1, 0, -1, 1, 1, -1, 1, 1, -1, 1, 1, -1, 0, -1, 1, -1, 
                  -1, 1, 1, -1, 1, 1, 1, 0, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 0, 1, 
                  1, 1, -1, -1, -1,  1, 1, 1, 1, 0, -1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 
                  1, -1, 1, 1, -1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 1, 1, 1, 1]

# Function to process the data and create a BSON document
def create_phishing_document(feature_vector, feature_names):
    # Ensure the feature vector is trimmed to match the feature names
    # Taking only the first len(feature_names) elements
    trimmed_vector = feature_vector[:len(feature_names)]
    
    # Create a dictionary from feature names and values
    feature_dict = {feature_names[i]: trimmed_vector[i] for i in range(len(trimmed_vector))}
    
    # Add metadata
    feature_dict['timestamp'] = datetime.now()
    feature_dict['data_source'] = 'manual_input'
    
    return feature_dict

# Method 1: Connect to MongoDB via local drivers or direct connection
def save_to_mongodb_local(document):
    try:
        # Connect to a local MongoDB instance
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["phishing_database"]
        collection = db["phishing_features"]
        
        # Insert the document
        result = collection.insert_one(document)
        
        print(f"Document inserted with ID: {result.inserted_id} via local connection")
        return result.inserted_id
    except Exception as e:
        print(f"Error connecting to local MongoDB: {e}")
        return None
    finally:
        if 'client' in locals():
            client.close()

# Method 2: Connect to MongoDB Atlas cluster
def save_to_mongodb_cluster(document):
    try:
        # Replace with your MongoDB Atlas connection string
        # Format: mongodb+srv://<username>:<password>@<cluster-address>/test?retryWrites=true&w=majority
        connection_string = "mongodb+srv://username:password@cluster0.mongodb.net/phishing_database?retryWrites=true&w=majority"
        
        client = pymongo.MongoClient(connection_string)
        db = client["phishing_database"]
        collection = db["phishing_features"]
        
        # Test connection
        client.admin.command('ping')
        print("Connected successfully to MongoDB Atlas cluster")
        
        # Insert the document
        result = collection.insert_one(document)
        
        print(f"Document inserted with ID: {result.inserted_id} via Atlas cluster")
        return result.inserted_id
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {e}")
        return None
    finally:
        if 'client' in locals():
            client.close()

# Process data and create BSON document
document = create_phishing_document(feature_vector, feature_names)
print("Created BSON document:")
print(document)

# Choose your connection method:
# 1. Uncomment to save via local MongoDB
# save_to_mongodb_local(document)

# 2. Uncomment to save via MongoDB Atlas cluster
# Make sure to update the connection string first!
# save_to_mongodb_cluster(document)

# Example of how to use both methods
def save_to_both_connections(document):
    local_id = save_to_mongodb_local(document)
    cluster_id = save_to_mongodb_cluster(document)
    
    print(f"Document saved to local MongoDB with ID: {local_id}")
    print(f"Document saved to MongoDB Atlas with ID: {cluster_id}")

# Uncomment to use both connection methods
# save_to_both_connections(document)