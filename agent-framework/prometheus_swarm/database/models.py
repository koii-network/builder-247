"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class TransactionStatus(str, Enum):
    """Enum for transaction status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionTracking(SQLModel, table=True):
    """Transaction tracking model for monitoring transaction lifecycles."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata fields
    workflow_name: Optional[str] = None
    initiator: Optional[str] = None
    extra_info: Optional[str] = None  # JSON-encoded additional details


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