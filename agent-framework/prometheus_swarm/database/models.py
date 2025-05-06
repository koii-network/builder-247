"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


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


class TransactionTracking(SQLModel, table=True):
    """Transaction tracking model to monitor and trace transactions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    status: str = Field(default="PENDING")  # e.g., PENDING, PROCESSING, COMPLETED, FAILED
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    source: Optional[str] = None  # Origin of the transaction
    destination: Optional[str] = None  # Destination of the transaction
    payload_type: Optional[str] = None  # Type of payload being processed
    payload_size: Optional[int] = None  # Size of payload in bytes
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    transaction_metadata: Optional[str] = None  # JSON or string for additional metadata

    @classmethod
    def create_transaction(
        cls,
        transaction_id: str,
        source: Optional[str] = None,
        destination: Optional[str] = None,
        payload_type: Optional[str] = None,
        payload_size: Optional[int] = None,
        transaction_metadata: Optional[str] = None
    ) -> "TransactionTracking":
        """
        Create a new transaction entry.

        Args:
            transaction_id (str): Unique identifier for the transaction
            source (Optional[str]): Origin of the transaction
            destination (Optional[str]): Destination of the transaction
            payload_type (Optional[str]): Type of payload being processed
            payload_size (Optional[int]): Size of payload in bytes
            transaction_metadata (Optional[str]): Additional transaction details

        Returns:
            TransactionTracking: The created transaction tracking instance
        """
        return cls(
            transaction_id=transaction_id,
            source=source,
            destination=destination,
            payload_type=payload_type,
            payload_size=payload_size,
            transaction_metadata=transaction_metadata
        )