from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnection:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(mongo_uri)
    
    def get_database(self, db_name: str):
        return self.client[db_name]
    
    def close(self):
        self.client.close()

from .mongo_connection import MongoConnection

mongo_conn = MongoConnection()

def insert_task_to_mongodb(task: Task) -> bool:
    try:
        # Get the database and collection
        db = mongo_conn.get_database("builder247")
        todos_collection = db["todos"]
        
        # Insert the task
        result = todos_collection.insert_one(task.to_dict())
        
        # Check if the insertion was successful
        return result.acknowledged
    
    except ConnectionFailure:
        print("MongoDB connection failed")
        return False
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        return False
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        return False