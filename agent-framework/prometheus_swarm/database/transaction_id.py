from sqlmodel import SQLModel, Field, Column, DateTime
from sqlalchemy.sql import func
from datetime import datetime

class TransactionID(SQLModel, table=True):
    """
    Database model for storing and tracking transaction IDs.
    
    Attributes:
        id (int): Primary key for the transaction record
        transaction_id (str): Unique identifier for the transaction
        context (str): Context or type of transaction
        timestamp (DateTime): Timestamp of transaction creation
        status (str): Current status of the transaction
        additional_info (str, optional): Additional metadata about the transaction
    """
    __tablename__ = 'transaction_ids'

    id: int = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    context: str
    timestamp: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    status: str = Field(default='pending')
    additional_info: str = Field(default=None, nullable=True)

    @classmethod
    def create(cls, transaction_id: str, context: str, status: str = 'pending', additional_info: str = None):
        """
        Class method to create a new transaction ID record.
        
        Args:
            transaction_id (str): Unique transaction identifier
            context (str): Transaction context
            status (str, optional): Transaction status. Defaults to 'pending'
            additional_info (str, optional): Additional transaction metadata
        
        Returns:
            TransactionID: New transaction record
        """
        return cls(
            transaction_id=transaction_id,
            context=context,
            status=status,
            additional_info=additional_info
        )

    def update_status(self, new_status: str):
        """
        Update the status of the transaction.
        
        Args:
            new_status (str): New status to set for the transaction
        """
        self.status = new_status

    def __repr__(self):
        """
        String representation of the TransactionID.
        
        Returns:
            str: Formatted string with transaction details
        """
        return f"<TransactionID(id={self.id}, transaction_id='{self.transaction_id}', context='{self.context}', status='{self.status}')>"