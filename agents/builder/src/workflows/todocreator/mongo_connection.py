from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

load_dotenv()


class MongoConnection:
    def __init__(self, mongo_uri: str = os.getenv("MONGO_URI")):
        self.client = MongoClient(mongo_uri)
    
    def get_database(self, db_name: str):
        return self.client[db_name]
    
    def close(self):
        self.client.close()
