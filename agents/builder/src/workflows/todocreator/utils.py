from pydantic import BaseModel, Field
from typing import List
import uuid
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from .mongo_connection import MongoConnection

mongo_conn = MongoConnection()
db = mongo_conn.get_database("builder247")
todos_collection = db["todos"]
class TaskModel(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    repoOwner: str = Field(..., description="Repository owner")
    repoName: str = Field(..., description="Repository name")
    status: str = Field(default="Initialized", description="Task status")
    assignedTo: List[str] = Field(default=[], description="List of assigned to")

    def to_dict(self):
        """Convert Task object to dictionary format for storing in MongoDB"""
        return self.model_dump()


def insert_task_to_mongodb(task: TaskModel) -> bool:
    try:
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
    
def get_all_tasks_title_uuid_from_mongodb() -> List[dict]:
    try:
        # Get all tasks from MongoDB
        tasks = todos_collection.find({}, {"_id": 0, "title": 1, "uuid": 1})
        
        # Convert cursor to list of dictionaries with only 'uuid' and 'title'
        return [{"uuid": task["uuid"], "title": task["title"]} for task in tasks]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    task = TaskModel(title="Test Task", description="This is a test task", acceptance_criteria=["Test acceptance criteria"], repoOwner="Test Owner", repoName="Test Name")
    insert_task_to_mongodb(task)