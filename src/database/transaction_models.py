from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    REWARD = "reward"

class Transaction(Base):
    """
    Represents a financial transaction in the system.
    Tracks details of monetary movements between accounts or systems.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reference_code = Column(String(50), unique=True, nullable=False)
    
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>"

def create_transaction(
    session, 
    transaction_type: TransactionType, 
    amount: float, 
    currency: str, 
    sender_id: int = None, 
    recipient_id: int = None, 
    description: str = None
) -> Transaction:
    """
    Create and save a new transaction.
    
    Args:
        session: SQLAlchemy database session
        transaction_type: Type of transaction
        amount: Transaction amount
        currency: Currency of the transaction
        sender_id: Optional ID of the sender
        recipient_id: Optional ID of the recipient
        description: Optional transaction description
    
    Returns:
        Saved Transaction object
    """
    import uuid

    transaction = Transaction(
        transaction_type=transaction_type,
        amount=amount,
        currency=currency,
        sender_id=sender_id,
        recipient_id=recipient_id,
        description=description,
        reference_code=str(uuid.uuid4()),
        status=TransactionStatus.PENDING
    )
    
    session.add(transaction)
    session.commit()
    
    return transaction