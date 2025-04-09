from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = 'mongodb://abhishek:0LiWdFRno2XWIGaP@cluster0-shard-00-00.yanlm.mongodb.net:27017,cluster0-shard-00-01.yanlm.mongodb.net:27017,cluster0-shard-00-02.yanlm.mongodb.net:27017/?ssl=true&replicaSet=atlas-nox15r-shard-0&authSource=admin&retryWrites=true&w=majority'

client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Select the database and collection
db = client['sheet2']  # Replace 'myDatabase' with your database name
collection = db['sheet2']  # Replace 'sales' with your collection name

# Insert data
data = [
    { 'item': 'laptop', 'price': 1000, 'quantity': 3 },
    { 'item': 'phone', 'price': 500, 'quantity': 5 },
    { 'item': 'tablet', 'price': 300, 'quantity': 7 },
    { 'item': 'monitor', 'price': 200, 'quantity': 4 },
    { 'item': 'keyboard', 'price': 50, 'quantity': 10 },
]

result = collection.insert_many(data)
print(f"Inserted {len(result.inserted_ids)} documents into the sales collection.")