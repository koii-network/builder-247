from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TransactionID(Base):
    """
    Model representing a transaction ID with comprehensive tracking and metadata.
    
    Attributes:
        id (int): Primary key for the transaction record
        transaction_id (str): Unique identifier for the transaction
        source (str): Origin or system generating the transaction
        status (str): Current status of the transaction (e.g., pending, completed, failed)
        created_at (datetime): Timestamp of transaction creation
        updated_at (datetime): Timestamp of last update
        is_processed (bool): Flag indicating whether the transaction has been processed
        metadata (dict): Additional JSON-stored metadata about the transaction
    """
    __tablename__ = 'transaction_ids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)

    def __repr__(self):
        """
        String representation of the TransactionID instance.
        
        Returns:
            str: Formatted string with key transaction details
        """
        return (f"&lt;TransactionID(transaction_id='{self.transaction_id}', "
                f"source='{self.source}', status='{self.status}', "
                f"processed={self.is_processed})&gt;")

def create_transaction_id_table(engine):
    """
    Create the transaction ID table in the database.
    
    Args:
        engine: SQLAlchemy database engine
    """
    Base.metadata.create_all(engine)