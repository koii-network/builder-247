from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import json

Base = declarative_base()

class Conversation(Base):
    """
    Represents a conversation entity
    """
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """
    Represents a message in a conversation
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")

class Log(Base):
    """
    Represents a log entry
    """
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    level = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TransactionID(Base):
    """
    A model to store and manage transaction IDs with comprehensive tracking.
    
    Attributes:
        id (int): Primary key for database
        transaction_uuid (str): Unique identifier for the transaction
        created_at (datetime): Timestamp of transaction creation
        updated_at (datetime): Timestamp of last transaction update
        status (str): Current status of the transaction
        is_completed (bool): Flag indicating transaction completion
        transaction_metadata (str): Optional JSON-serializable metadata for additional context
    """
    __tablename__ = 'transaction_ids'

    id = Column(Integer, primary_key=True)
    transaction_uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default='PENDING')
    is_completed = Column(Boolean, default=False)
    transaction_metadata = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint('transaction_uuid', name='uq_transaction_uuid'),
    )

    def __repr__(self):
        return f"<TransactionID(uuid='{self.transaction_uuid}', status='{self.status}')>"

    @classmethod
    def create_transaction(cls, status='PENDING', transaction_metadata=None):
        """
        Class method to create a new transaction with optional status and metadata.
        
        Args:
            status (str, optional): Initial transaction status. Defaults to 'PENDING'.
            transaction_metadata (dict or str, optional): Additional transaction metadata. Defaults to None.
        
        Returns:
            TransactionID: A new transaction instance
        """
        # Convert dict to JSON if a dictionary is passed
        if isinstance(transaction_metadata, dict):
            transaction_metadata = json.dumps(transaction_metadata)
        
        return cls(
            status=status,
            transaction_metadata=transaction_metadata
        )

    def mark_completed(self):
        """
        Mark the transaction as completed.
        """
        self.is_completed = True
        self.status = 'COMPLETED'

    def update_status(self, new_status):
        """
        Update the transaction status.
        
        Args:
            new_status (str): New status for the transaction
        """
        self.status = new_status

    def get_metadata(self):
        """
        Parse and return the metadata as a dictionary.
        
        Returns:
            dict or None: Parsed metadata or None if no metadata exists
        """
        if self.transaction_metadata:
            try:
                return json.loads(self.transaction_metadata)
            except (json.JSONDecodeError, TypeError):
                return None
        return None