from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class Transaction:
    """
    Represents a transaction with essential tracking information.
    """
    id: str
    amount: float
    description: str
    timestamp: datetime
    category: Optional[str] = None
    status: str = 'pending'

class TransactionDataAccessLayer:
    """
    Data Access Layer for managing transaction records.
    Provides methods for CRUD operations on transactions.
    """
    def __init__(self):
        """
        Initialize the Transaction Data Access Layer with an empty transaction store.
        """
        self._transactions: Dict[str, Transaction] = {}

    def create_transaction(self, amount: float, description: str, 
                            category: Optional[str] = None) -> Transaction:
        """
        Create a new transaction and store it.

        Args:
            amount (float): Transaction amount
            description (str): Transaction description
            category (Optional[str], optional): Transaction category. Defaults to None.

        Returns:
            Transaction: The created transaction
        """
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")

        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            id=transaction_id,
            amount=amount,
            description=description,
            timestamp=datetime.now(),
            category=category
        )
        
        self._transactions[transaction_id] = transaction
        return transaction

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve a transaction by its ID.

        Args:
            transaction_id (str): Unique identifier of the transaction

        Returns:
            Optional[Transaction]: The transaction if found, otherwise None
        """
        return self._transactions.get(transaction_id)

    def update_transaction(self, transaction_id: str, 
                           amount: Optional[float] = None, 
                           description: Optional[str] = None, 
                           category: Optional[str] = None,
                           status: Optional[str] = None) -> Optional[Transaction]:
        """
        Update an existing transaction.

        Args:
            transaction_id (str): ID of the transaction to update
            amount (Optional[float], optional): New transaction amount
            description (Optional[str], optional): New transaction description
            category (Optional[str], optional): New transaction category
            status (Optional[str], optional): New transaction status

        Returns:
            Optional[Transaction]: Updated transaction or None if not found
        """
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            return None

        if amount is not None:
            if amount <= 0:
                raise ValueError("Transaction amount must be positive")
            transaction.amount = amount

        if description is not None:
            transaction.description = description

        if category is not None:
            transaction.category = category

        if status is not None:
            transaction.status = status

        return transaction

    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Delete a transaction by its ID.

        Args:
            transaction_id (str): ID of the transaction to delete

        Returns:
            bool: True if transaction was deleted, False if not found
        """
        if transaction_id in self._transactions:
            del self._transactions[transaction_id]
            return True
        return False

    def list_transactions(self, category: Optional[str] = None, 
                          status: Optional[str] = None) -> List[Transaction]:
        """
        List transactions with optional filtering by category and status.

        Args:
            category (Optional[str], optional): Filter by category
            status (Optional[str], optional): Filter by status

        Returns:
            List[Transaction]: List of matching transactions
        """
        transactions = list(self._transactions.values())
        
        if category is not None:
            transactions = [t for t in transactions if t.category == category]
        
        if status is not None:
            transactions = [t for t in transactions if t.status == status]
        
        return transactions