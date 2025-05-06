from typing import List, Any, Dict

class TransactionDuplicationError(Exception):
    """Raised when a transaction with a duplicate ID is detected."""
    pass

def check_transaction_id_duplicate(transactions: List[Dict[str, Any]], transaction_id: str) -> bool:
    """
    Check if a transaction ID already exists in a list of transactions.

    Args:
        transactions (List[Dict[str, Any]]): A list of transaction dictionaries
        transaction_id (str): The transaction ID to check for duplication

    Returns:
        bool: True if the transaction ID is a duplicate, False otherwise

    Raises:
        ValueError: If transactions is None or transaction_id is empty/None
    """
    # Input validation
    if transactions is None:
        raise ValueError("Transactions list cannot be None")
    
    if not transaction_id:
        raise ValueError("Transaction ID cannot be empty")

    # Check for duplicates
    duplicate_transactions = [
        transaction for transaction in transactions 
        if transaction.get('transaction_id') == transaction_id
    ]

    return len(duplicate_transactions) > 0

def add_transaction_with_duplicate_check(
    transactions: List[Dict[str, Any]], 
    new_transaction: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Add a new transaction to the list after checking for duplicates.

    Args:
        transactions (List[Dict[str, Any]]): Existing list of transactions
        new_transaction (Dict[str, Any]): New transaction to add

    Returns:
        List[Dict[str, Any]]: Updated list of transactions

    Raises:
        TransactionDuplicationError: If a transaction with the same ID already exists
        ValueError: If inputs are invalid
    """
    # Input validation
    if transactions is None:
        transactions = []

    if not isinstance(new_transaction, dict):
        raise ValueError("New transaction must be a dictionary")

    transaction_id = new_transaction.get('transaction_id')
    
    if not transaction_id:
        raise ValueError("Transaction must have a transaction_id")

    # Check for duplicates before adding
    if check_transaction_id_duplicate(transactions, transaction_id):
        raise TransactionDuplicationError(f"Transaction with ID {transaction_id} already exists")

    # Add the new transaction
    transactions.append(new_transaction)
    return transactions