import logging
logging.basicConfig(level=logging.DEBUG)

from pymongo import MongoClient

uri = "mongodb://abhishek:0LiWdFRno2XWIGaP@cluster0.yanlm.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)