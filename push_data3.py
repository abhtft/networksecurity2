
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://akdbgbr:Star123@cluster0-shard-00-00.spzn0.mongodb.net:27017,cluster0-shard-00-01.spzn0.mongodb.net:27017,cluster0-shard-00-02.spzn0.mongodb.net:27017/?replicaSet=atlas-mtp2v2-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)