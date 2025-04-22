"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from sqlalchemy import Column
from prometheus_swarm.database.models import Conversation, Message, Log


class Submission(SQLModel, table=True):
    """Task submission model."""

    task_id: str
    round_number: int = Field(primary_key=True)
    status: str = "pending"
    pr_url: Optional[str] = None
    username: Optional[str] = None
    repo_urls: Optional[dict] = Field(
        default=None, sa_column=Column(JSON)
    )  # Store as JSON type
    repo_url: Optional[str] = None