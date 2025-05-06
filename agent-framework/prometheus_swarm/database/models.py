"""Database models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from sqlmodel import SQLModel, Field, Relationship, Column, String


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
    """Transaction tracking model to track unique transactions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    status: str = Field(description="Status of the transaction (e.g., 'pending', 'completed', 'failed')")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    transaction_metadata: Optional[str] = Field(default=None, sa_column=Column(String), description="JSON string of transaction metadata")
    source: Optional[str] = Field(description="Source or origin of the transaction")
    
    @classmethod
    def create_transaction(cls, transaction_id: str, source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> 'TransactionTracking':
        """
        Create a new transaction with a unique transaction ID.
        
        Args:
            transaction_id (str): A unique identifier for the transaction
            source (Optional[str]): Source or origin of the transaction
            metadata (Optional[Dict[str, Any]]): Additional metadata for the transaction
        
        Returns:
            TransactionTracking: The created transaction instance
        """
        return cls(
            transaction_id=transaction_id,
            status='pending',
            source=source,
            transaction_metadata=json.dumps(metadata) if metadata else None
        )
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata as a dictionary.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed metadata or None
        """
        return json.loads(self.transaction_metadata) if self.transaction_metadata else None
    
    def update_status(self, new_status: str):
        """
        Update the status of the transaction.
        
        Args:
            new_status (str): New status for the transaction
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()