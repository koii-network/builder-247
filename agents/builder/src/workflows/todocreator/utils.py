from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from .mongo_connection import MongoConnection
from enum import Enum

mongo_conn = MongoConnection()
db = mongo_conn.get_database("builder247")
todos_collection = db["todos"]
issues_collection = db["issues"]

class TodoStatus(str, Enum):
    INITIALIZED = "initialized"  # Means not assigned to any node or when a node is audited as false
    IN_PROGRESS = "in_progress"  # Means is assigned to a node, not completed
    AUDITED = "audited"         # Means a PR is audited and waiting for merge
    MERGED = "merged"           # Means a PR is merged

class TaskAssignedInfo(BaseModel):
    stakingKey: str = Field(..., description="Staking key of the assigned agent")
    pubkey: str = Field(..., description="Public key of the assigned agent")
    taskId: str = Field(..., description="Task ID")
    roundNumber: int = Field(..., description="Round number")
    githubUsername: str = Field(..., description="GitHub username")
    prUrl: Optional[str] = Field(None, description="Pull request URL")
    todoSignature: Optional[str] = Field(None, description="Todo signature")
    prSignature: Optional[str] = Field(None, description="PR signature")
    auditSignature: Optional[str] = Field(None, description="Audit signature")
    auditResult: Optional[bool] = Field(None, description="Audit result")

class TaskModel(BaseModel):
    title: str = Field(..., description="Task title")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    issueUuid: str = Field(..., description="Issue UUID")
    description: str = Field(..., description="Task description")
    acceptanceCriteria: str = Field(..., description="Acceptance criteria")
    repoOwner: str = Field(..., description="Repository owner")
    repoName: str = Field(..., description="Repository name")
    assignedTo: List[TaskAssignedInfo] = Field(default=[], description="List of assigned agents")
    dependencyTasks: List[str] = Field(default=[], description="List of dependency tasks")
    status: TodoStatus = Field(default=TodoStatus.INITIALIZED, description="Task status")

    def to_dict(self):
        """Convert Task object to dictionary format for storing in MongoDB"""
        return self.model_dump()


class AggregatorInfo(BaseModel):
    agent: str = Field(..., description="Aggregator agent")
    timestamp: int = Field(..., description="Timestamp of aggregator assignment")

class IssueStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    # Add other status values as needed

class AssignedInfo(BaseModel):
    stakingKey: str = Field(..., description="Staking key of the assigned agent")
    pubkey: str = Field(..., description="Public key of the assigned agent")
    taskId: str = Field(..., description="Task ID")
    roundNumber: int = Field(..., description="Round number")
    githubUsername: str = Field(..., description="GitHub username")
    prUrl: Optional[str] = Field(None, description="Pull request URL")
    todoSignature: Optional[str] = Field(None, description="Todo signature")
    prSignature: Optional[str] = Field(None, description="PR signature")
    auditSignature: Optional[str] = Field(None, description="Audit signature")
    auditResult: Optional[bool] = Field(None, description="Audit result")

class IssueModel(BaseModel):
    title: Optional[str] = Field(None, description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    repoOwner: str = Field(..., description="Repository owner")
    repoName: str = Field(..., description="Repository name")
    status: IssueStatus = Field(default=IssueStatus.INITIALIZED, description="Issue status")
    aggregator: Optional[AggregatorInfo] = Field(None, description="Aggregator information")
    leaderDecidedRound: Optional[int] = Field(None, description="Leader decided round")
    assignedTo: List[AssignedInfo] = Field(default=[], description="List of assigned agents")

    def to_dict(self):
        """Convert Issue object to dictionary format for storing in MongoDB"""
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
def insert_issue_to_mongodb(issue: IssueModel) -> bool:
    try:
        # Insert the issue
        result = issues_collection.insert_one(issue.to_dict())
        
        # Check if the insertion was successful
        return result.acknowledged
    except ConnectionFailure:
        print("MongoDB connection failed")
        return False
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        return False
    
if __name__ == "__main__":
    task = TaskModel(
        title="Test Task",
        description="This is a test task",
        acceptanceCriteria="Test acceptance criteria",
        repoOwner="Test Owner",
        repoName="Test Name",
        issueUuid="test-issue-uuid"
    )
    insert_task_to_mongodb(task)
    issue = IssueModel(
        title="Test Issue",
        description="This is a test issue",
        repoOwner="Test Owner",
        repoName="Test Name"
    )
    insert_issue_to_mongodb(issue)