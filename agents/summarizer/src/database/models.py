"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from sqlalchemy import Column


class Conversation(SQLModel, table=True):
    """Conversation model."""

    id: str = Field(primary_key=True)
    model: str
    system_prompt: Optional[str] = None
    available_tools: Optional[str] = None  # JSON list of tool names
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model."""

    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str
    content: str  # JSON-encoded content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation: Conversation = Relationship(back_populates="messages")


class Submission(SQLModel, table=True):
    """Task submission model."""

    task_id: str
    round_number: int = Field(primary_key=True)
    status: str = "pending"
    pr_url: Optional[str] = None
    username: Optional[str] = None
    repo_urls: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Store as JSON type
    repo_url: Optional[str] = None

class Log(SQLModel, table=True):
    """Log entry model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    path: Optional[str] = None
    line_no: Optional[int] = None
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[str] = None
