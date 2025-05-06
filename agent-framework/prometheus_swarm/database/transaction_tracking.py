from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime

Base = declarative_base()

class Transaction(Base):
    """
    SQLAlchemy model representing a transaction in the tracking system.
    
    Attributes:
        id (int): Unique identifier for the transaction
        transaction_type (str): Type of transaction 
        amount (float): Transaction amount
        timestamp (datetime): Time of the transaction
        metadata (dict): Additional transaction metadata
        status (str): Current status of the transaction
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    status = Column(String, default='pending')

class TransactionAccessLayer:
    """
    Data Access Layer for managing transaction records.
    
    Provides methods for creating, retrieving, updating, and deleting 
    transaction records in the database.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the Transaction Access Layer with a database session.
        
        Args:
            session (Session): SQLAlchemy database session
        """
        self.session = session
    
    def create_transaction(self, 
                           transaction_type: str, 
                           amount: float, 
                           metadata: Optional[Dict[str, Any]] = None, 
                           status: str = 'pending') -> Transaction:
        """
        Create a new transaction record.
        
        Args:
            transaction_type (str): Type of transaction
            amount (float): Transaction amount
            metadata (dict, optional): Additional transaction details
            status (str, optional): Transaction status, defaults to 'pending'
        
        Returns:
            Transaction: The created transaction object
        
        Raises:
            ValueError: If transaction type or amount is invalid
        """
        if not transaction_type:
            raise ValueError("Transaction type cannot be empty")
        
        if amount < 0:
            raise ValueError("Transaction amount must be non-negative")
        
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            metadata=metadata or {},
            status=status
        )
        
        self.session.add(transaction)
        self.session.commit()
        
        return transaction
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Retrieve a transaction by its ID.
        
        Args:
            transaction_id (int): Unique identifier of the transaction
        
        Returns:
            Transaction or None: The transaction if found, otherwise None
        """
        return self.session.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_transactions_by_type(self, transaction_type: str) -> List[Transaction]:
        """
        Retrieve all transactions of a specific type.
        
        Args:
            transaction_type (str): Type of transactions to retrieve
        
        Returns:
            List[Transaction]: List of transactions matching the type
        """
        return self.session.query(Transaction).filter(Transaction.transaction_type == transaction_type).all()
    
    def update_transaction_status(self, transaction_id: int, new_status: str) -> Optional[Transaction]:
        """
        Update the status of a specific transaction.
        
        Args:
            transaction_id (int): ID of the transaction to update
            new_status (str): New status for the transaction
        
        Returns:
            Transaction or None: Updated transaction if found, otherwise None
        
        Raises:
            ValueError: If new status is empty
        """
        if not new_status:
            raise ValueError("Transaction status cannot be empty")
        
        transaction = self.get_transaction_by_id(transaction_id)
        
        if transaction:
            transaction.status = new_status
            self.session.commit()
        
        return transaction
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction by its ID.
        
        Args:
            transaction_id (int): ID of the transaction to delete
        
        Returns:
            bool: True if transaction was deleted, False if not found
        """
        transaction = self.get_transaction_by_id(transaction_id)
        
        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        
        return False