"""Database models."""

from sqlmodel import SQLModel, Field
from typing import Optional


class Submission(SQLModel, table=True):
    """Task submission model."""

    task_id: str = Field(primary_key=True)
    round_number: int = Field(primary_key=True)
    status: str = "pending"
    pr_url: Optional[str] = None
    username: Optional[str] = None
    repo_owner: str
    repo_name: str
    uuid: Optional[str] = None  # UUID of the issue/todo
    node_type: str = "worker"  # Either "worker" or "leader"
