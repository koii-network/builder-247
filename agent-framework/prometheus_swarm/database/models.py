"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, String, DateTime


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
    """
    Model to track transaction IDs across the system.
    
    Helps in tracing the lifecycle and status of transactions.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    workflow_type: str  # e.g., 'task', 'audit', 'submission'
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional metadata to provide context about the transaction
    source_module: Optional[str] = None
    request_details: Optional[str] = None  # JSON-encoded additional details
    error_message: Optional[str] = None
    
    @classmethod
    def create_transaction(
        cls,
        transaction_id: str,
        workflow_type: str,
        source_module: Optional[str] = None,
        request_details: Optional[str] = None
    ) -> 'TransactionTracking':
        """
        Create a new transaction tracking entry.
        
        Args:
            transaction_id: Unique identifier for the transaction
            workflow_type: Type of workflow this transaction belongs to
            source_module: Optional module initiating the transaction
            request_details: Optional JSON-encoded request details
        
        Returns:
            A new TransactionTracking instance
        """
        return cls(
            transaction_id=transaction_id,
            workflow_type=workflow_type,
            status='pending',
            source_module=source_module,
            request_details=request_details
        )
    
    def update_status(self, new_status: str, error_message: Optional[str] = None) -> None:
        """
        Update the status of a transaction.
        
        Args:
            new_status: New status of the transaction
            error_message: Optional error message if transaction failed
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message