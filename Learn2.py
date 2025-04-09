from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB Atlas
uri = "mongodb+srv://abhishek:0LiWdFRno2XWIGaP@cluster0.yanlm.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# Select the database and collection
db = client['myDatabase']
sales_collection = db['sales']

# Insert data
sales_data = [
    { 'item': 'abc', 'price': 10, 'quantity': 2, 'date': datetime(2014, 3, 1, 8, 0, 0) },
    { 'item': 'jkl', 'price': 20, 'quantity': 1, 'date': datetime(2014, 3, 1, 9, 0, 0) },
    { 'item': 'xyz', 'price': 5, 'quantity': 10, 'date': datetime(2014, 3, 15, 9, 0, 0) },
    { 'item': 'xyz', 'price': 5, 'quantity': 20, 'date': datetime(2014, 4, 4, 11, 21, 39) },
    { 'item': 'abc', 'price': 10, 'quantity': 10, 'date': datetime(2014, 4, 4, 21, 23, 13) },
    { 'item': 'def', 'price': 7.5, 'quantity': 5, 'date': datetime(2015, 6, 4, 5, 8, 13) },
    { 'item': 'def', 'price': 7.5, 'quantity': 10, 'date': datetime(2015, 9, 10, 8, 43, 0) },
    { 'item': 'abc', 'price': 10, 'quantity': 5, 'date': datetime(2016, 2, 6, 20, 20, 13) },
]

result = sales_collection.insert_many(sales_data)
print(f"Inserted {len(result.inserted_ids)} documents into the sales collection.")