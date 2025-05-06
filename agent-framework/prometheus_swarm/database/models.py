"""Database models."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import JSON as SAJSONType
from decimal import Decimal

# Existing models...

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
    metadata: Optional[dict] = Field(
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