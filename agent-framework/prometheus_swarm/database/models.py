"""Database models."""

from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship, JSON
from enum import Enum, auto


class TransactionStatus(Enum):
    """Enum for transaction status."""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class Transaction(SQLModel, table=True):
    """Transaction tracking model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Transaction Identification
    transaction_uuid: str = Field(unique=True, index=True)
    user_id: Optional[str] = Field(index=True)
    
    # Transaction Metadata
    transaction_type: str 
    description: Optional[str] = None
    
    # Transaction State
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Transaction Details
    details: Optional[Dict] = Field(default=None, sa_column_kwargs={"type_": JSON})
    
    # Tracking and Debugging
    source_system: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

    # Existing models from previous implementation...

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