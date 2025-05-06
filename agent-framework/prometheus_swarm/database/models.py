"""Database models."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import JSON as SAJSONType
from decimal import Decimal


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


class Transaction(SQLModel, table=True):
    """Transaction tracking model for comprehensive financial tracking."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_uuid: str = Field(unique=True, index=True)
    
    # Transaction details
    type: str = Field(description="Type of transaction (e.g., income, expense, transfer)")
    amount: Decimal = Field(description="Transaction amount")
    currency: str = Field(default="USD", description="Currency of the transaction")
    
    # Temporal information
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of transaction")
    
    # Status tracking
    status: str = Field(description="Current status of transaction (e.g., pending, completed, failed)")
    
    # Optional descriptive and referential fields
    description: Optional[str] = Field(default=None, description="Detailed description of transaction")
    category: Optional[str] = Field(default=None, description="Transaction category")
    
    # Metadata and references
    source: Optional[str] = Field(default=None, description="Source of transaction")
    destination: Optional[str] = Field(default=None, description="Destination of transaction")
    
    # Additional flexible metadata
    extra_metadata: Optional[dict] = Field(
        default=None, 
        sa_column=Column(SAJSONType, nullable=True),
        description="Additional transaction metadata"
    )
    
    # Auditing fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        """Configuration for Transaction model."""
        json_schema_extra = {
            "example": {
                "transaction_uuid": "tx_123456",
                "type": "income",
                "amount": 100.50,
                "currency": "USD",
                "status": "completed",
                "description": "Salary payment",
                "category": "salary"
            }
        }