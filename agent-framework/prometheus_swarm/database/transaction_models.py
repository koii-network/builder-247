from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class TransactionStatus(enum.Enum):
    """Enumeration of possible transaction statuses."""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELED = 'canceled'

class Transaction(Base):
    """
    Represents a financial or system transaction with comprehensive tracking.
    
    Attributes:
        id: Unique identifier for the transaction
        transaction_type: Type of transaction (e.g., payment, transfer, reward)
        amount: Monetary value of the transaction
        status: Current status of the transaction
        description: Detailed description of the transaction
        timestamp: Datetime when the transaction was created
        external_id: Optional external system reference ID
        metadata: Additional JSON/dictionary-like metadata for flexible tracking
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    external_id = Column(String(100), nullable=True, unique=True)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>"

class TransactionAuditLog(Base):
    """
    Tracks changes and events related to transactions for audit and traceability.
    
    Attributes:
        id: Unique identifier for the audit log entry
        transaction_id: Reference to the associated transaction
        action: Type of action performed
        actor: Entity or user who performed the action
        timestamp: Datetime of the action
        details: Additional details about the action
    """
    __tablename__ = 'transaction_audit_logs'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    action = Column(String(50), nullable=False)
    actor = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(255), nullable=True)
    
    transaction = relationship("Transaction", backref="audit_logs")
    
    def __repr__(self):
        return f"<TransactionAuditLog(id={self.id}, transaction_id={self.transaction_id}, action={self.action})>"