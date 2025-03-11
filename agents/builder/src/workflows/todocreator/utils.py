from pydantic import BaseModel, Field
from typing import List
import uuid
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

class Task(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    
    def to_dict(self):
        """Convert Task object to dictionary format for storing in MongoDB"""
        return self.model_dump()

def insert_task_to_mongodb(task: Task, mongo_uri: str = "mongodb://localhost:27017/") -> bool:
    """
    Insert a task into the 'todos' collection of the 'builder247' database in MongoDB.
    
    Parameters:
        task: The Task object to insert
        mongo_uri: MongoDB connection URI, defaults to local MongoDB
        
    Returns:
        bool: True if the insertion was successful, False otherwise
    """
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        
        # Check if the connection is successful
        client.admin.command('ping')
        
        # Get the database and collection
        db = client["builder247"]
        todos_collection = db["todos"]
        
        # Insert the task
        result = todos_collection.insert_one(task.to_dict())
        
        # Close the connection
        client.close()
        
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
