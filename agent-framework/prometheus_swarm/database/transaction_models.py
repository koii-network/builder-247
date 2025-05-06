from sqlalchemy import Column, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
import uuid

Base = declarative_base()

class Transaction(Base):
    """
    Represents a transaction with UUID-based tracking and precise timestamp management.
    """
    __tablename__ = 'transactions'

    # UUID transaction_id with unique constraint
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    
    # Created at timestamp with current timestamp as default
    created_at = Column(DateTime(timezone=True), 
                        nullable=False, 
                        server_default=text('CURRENT_TIMESTAMP(3)'))
    
    # Expiration timestamp with optional millisecond precision
    expiration_time = Column(DateTime(timezone=True), 
                             nullable=True, 
                             default=lambda: datetime.utcnow() + timedelta(hours=24))

    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_transaction_id_created_at', 'transaction_id', 'created_at'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, created_at={self.created_at})>"