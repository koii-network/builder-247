"""Database models."""

from datetime import datetime, UTC
from typing import Optional, List, ClassVar
from sqlmodel import SQLModel, Field, Relationship, Column, String, DECIMAL
from uuid import uuid4
from enum import Enum


class TransactionStatus(str, Enum):
    """Allowed transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Conversation(SQLModel, table=True):
    """Conversation model."""

    id: str = Field(primary_key=True)
    model: str
    system_prompt: Optional[str] = None
    available_tools: Optional[str] = None  # JSON list of tool names
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model."""

    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str
    content: str  # JSON-encoded content
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    conversation: Conversation = Relationship(back_populates="messages")


class Log(SQLModel, table=True):
    """Log entry model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
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


class Transaction(SQLModel, table=True):
    """Transaction tracking model."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    source: str
    destination: str
    amount: float = Field(sa_column=Column(DECIMAL(precision=20, scale=2)))
    currency: str
    transaction_type: str
    status: str = Field(default=TransactionStatus.PENDING)
    description: Optional[str] = None
    transaction_metadata: Optional[str] = None  # JSON-encoded additional data
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), 
        sa_column_kwargs={"onupdate": datetime.now(UTC)}
    )

    ALLOWED_STATUSES: ClassVar[List[str]] = [
        TransactionStatus.PENDING, 
        TransactionStatus.COMPLETED, 
        TransactionStatus.FAILED, 
        TransactionStatus.REFUNDED, 
        TransactionStatus.CANCELLED
    ]

    def __setattr__(self, name, value):
        """
        Override __setattr__ to validate transaction status.
        
        Args:
            name (str): Attribute name
            value (Any): Attribute value

        Raises:
            ValueError: If attempting to set an invalid transaction status
        """
        if name == 'status':
            if value not in self.ALLOWED_STATUSES:
                raise ValueError(
                    f"Invalid transaction status. Must be one of {self.ALLOWED_STATUSES}"
                )
        
        # Update updated_at when status changes
        if name == 'status':
            current_time = datetime.now(UTC)
            super().__setattr__('updated_at', current_time)
        
        super().__setattr__(name, value)