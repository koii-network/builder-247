"""
Data Access Layer for Transaction Tracking

This module provides an interface for managing and tracking transactions
with support for CRUD operations and basic transaction validation.
"""

from typing import Dict, List, Optional, Union
from datetime import datetime, timezone


class TransactionDAL:
    """
    Data Access Layer for Transaction Management
    
    Provides methods to create, read, update, and delete transactions
    with basic validation and tracking capabilities.
    """

    def __init__(self):
        """
        Initialize the Transaction Data Access Layer.
        Uses an in-memory list to store transactions for demonstration.
        """
        self._transactions: List[Dict[str, Union[str, float, datetime]]] = []
        self._next_id = 1

    def create_transaction(
        self, 
        amount: float, 
        description: str, 
        transaction_type: str
    ) -> Dict[str, Union[str, float, datetime]]:
        """
        Create a new transaction with validation.
        
        Args:
            amount (float): Transaction amount (must be non-negative)
            description (str): Transaction description
            transaction_type (str): Type of transaction (e.g., 'credit', 'debit')
        
        Returns:
            Dict containing transaction details
        
        Raises:
            ValueError: If amount is negative or transaction type is invalid
        """
        # Validate inputs
        if amount < 0:
            raise ValueError("Transaction amount must be non-negative")
        
        if not description or not description.strip():
            raise ValueError("Transaction description cannot be empty")
        
        # Validate transaction type
        valid_types = ['credit', 'debit', 'transfer']
        if transaction_type.lower() not in valid_types:
            raise ValueError(f"Invalid transaction type. Must be one of {valid_types}")

        # Create transaction
        transaction = {
            'id': str(self._next_id),
            'amount': amount,
            'description': description,
            'type': transaction_type.lower(),
            'timestamp': datetime.now(timezone.utc)
        }
        
        self._transactions.append(transaction)
        self._next_id += 1
        
        return transaction

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Union[str, float, datetime]]]:
        """
        Retrieve a transaction by its ID.
        
        Args:
            transaction_id (str): Unique identifier of the transaction
        
        Returns:
            Dict with transaction details or None if not found
        """
        for transaction in self._transactions:
            if transaction['id'] == transaction_id:
                return transaction
        return None

    def list_transactions(
        self, 
        limit: Optional[int] = None, 
        transaction_type: Optional[str] = None
    ) -> List[Dict[str, Union[str, float, datetime]]]:
        """
        List transactions with optional filtering.
        
        Args:
            limit (Optional[int]): Maximum number of transactions to return
            transaction_type (Optional[str]): Filter by transaction type
        
        Returns:
            List of transactions matching the criteria
        """
        filtered_transactions = self._transactions

        # Filter by transaction type if specified
        if transaction_type:
            filtered_transactions = [
                t for t in filtered_transactions 
                if t['type'].lower() == transaction_type.lower()
            ]

        # Apply limit if specified
        if limit is not None:
            filtered_transactions = filtered_transactions[:limit]

        return filtered_transactions

    def update_transaction(
        self, 
        transaction_id: str, 
        amount: Optional[float] = None,
        description: Optional[str] = None
    ) -> Optional[Dict[str, Union[str, float, datetime]]]:
        """
        Update an existing transaction.
        
        Args:
            transaction_id (str): ID of transaction to update
            amount (Optional[float]): New transaction amount
            description (Optional[str]): New transaction description
        
        Returns:
            Updated transaction or None if not found
        """
        transaction = self.get_transaction(transaction_id)
        
        if not transaction:
            return None

        # Validate and update amount if provided
        if amount is not None:
            if amount < 0:
                raise ValueError("Transaction amount must be non-negative")
            transaction['amount'] = amount

        # Update description if provided
        if description is not None:
            if not description or not description.strip():
                raise ValueError("Transaction description cannot be empty")
            transaction['description'] = description

        return transaction

    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Delete a transaction by its ID.
        
        Args:
            transaction_id (str): ID of transaction to delete
        
        Returns:
            bool: True if deleted, False if not found
        """
        for index, transaction in enumerate(self._transactions):
            if transaction['id'] == transaction_id:
                del self._transactions[index]
                return True
        
        return False