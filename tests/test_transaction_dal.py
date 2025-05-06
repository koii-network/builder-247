"""
Unit tests for Transaction Data Access Layer
"""

import pytest
from datetime import datetime, timezone
from src.transaction_dal import TransactionDAL


@pytest.fixture
def transaction_dal():
    """Fixture to create a fresh TransactionDAL for each test"""
    return TransactionDAL()


def test_create_transaction(transaction_dal):
    """Test creating a transaction successfully"""
    transaction = transaction_dal.create_transaction(
        amount=100.50, 
        description="Test Expense", 
        transaction_type="debit"
    )
    
    assert transaction['id'] == '1'
    assert transaction['amount'] == 100.50
    assert transaction['description'] == "Test Expense"
    assert transaction['type'] == "debit"
    assert isinstance(transaction['timestamp'], datetime)


def test_create_transaction_invalid_amount(transaction_dal):
    """Test creating a transaction with negative amount"""
    with pytest.raises(ValueError, match="Transaction amount must be non-negative"):
        transaction_dal.create_transaction(
            amount=-50, 
            description="Invalid Transaction", 
            transaction_type="debit"
        )


def test_create_transaction_invalid_description(transaction_dal):
    """Test creating a transaction with empty description"""
    with pytest.raises(ValueError, match="Transaction description cannot be empty"):
        transaction_dal.create_transaction(
            amount=50, 
            description="", 
            transaction_type="debit"
        )


def test_create_transaction_invalid_type(transaction_dal):
    """Test creating a transaction with invalid type"""
    with pytest.raises(ValueError, match="Invalid transaction type"):
        transaction_dal.create_transaction(
            amount=50, 
            description="Test Transaction", 
            transaction_type="invalid_type"
        )


def test_get_transaction(transaction_dal):
    """Test retrieving an existing transaction"""
    original = transaction_dal.create_transaction(
        amount=200, 
        description="Retrieval Test", 
        transaction_type="credit"
    )
    
    retrieved = transaction_dal.get_transaction(original['id'])
    assert retrieved == original


def test_get_nonexistent_transaction(transaction_dal):
    """Test retrieving a non-existent transaction"""
    result = transaction_dal.get_transaction('999')
    assert result is None


def test_list_transactions(transaction_dal):
    """Test listing transactions with and without filtering"""
    transaction_dal.create_transaction(100, "Debit Transaction", "debit")
    transaction_dal.create_transaction(200, "Credit Transaction", "credit")
    transaction_dal.create_transaction(300, "Another Debit", "debit")

    # List all transactions
    all_transactions = transaction_dal.list_transactions()
    assert len(all_transactions) == 3

    # List with limit
    limited_transactions = transaction_dal.list_transactions(limit=2)
    assert len(limited_transactions) == 2

    # List by type
    debit_transactions = transaction_dal.list_transactions(transaction_type="debit")
    assert len(debit_transactions) == 2
    assert all(t['type'] == 'debit' for t in debit_transactions)


def test_update_transaction(transaction_dal):
    """Test updating an existing transaction"""
    transaction = transaction_dal.create_transaction(
        amount=500, 
        description="Initial Transaction", 
        transaction_type="credit"
    )

    # Update amount
    updated = transaction_dal.update_transaction(
        transaction_id=transaction['id'], 
        amount=750
    )
    assert updated['amount'] == 750

    # Update description
    updated = transaction_dal.update_transaction(
        transaction_id=transaction['id'], 
        description="Updated Transaction"
    )
    assert updated['description'] == "Updated Transaction"


def test_update_invalid_transaction(transaction_dal):
    """Test updating a non-existent transaction"""
    result = transaction_dal.update_transaction('999', amount=100)
    assert result is None


def test_update_transaction_invalid_amount(transaction_dal):
    """Test updating transaction with invalid amount"""
    transaction = transaction_dal.create_transaction(
        amount=500, 
        description="Test Transaction", 
        transaction_type="credit"
    )

    with pytest.raises(ValueError, match="Transaction amount must be non-negative"):
        transaction_dal.update_transaction(
            transaction_id=transaction['id'], 
            amount=-100
        )


def test_delete_transaction(transaction_dal):
    """Test deleting an existing transaction"""
    transaction = transaction_dal.create_transaction(
        amount=300, 
        description="Delete Test", 
        transaction_type="debit"
    )

    # Verify deletion
    result = transaction_dal.delete_transaction(transaction['id'])
    assert result is True

    # Verify transaction is no longer retrievable
    retrieved = transaction_dal.get_transaction(transaction['id'])
    assert retrieved is None


def test_delete_nonexistent_transaction(transaction_dal):
    """Test deleting a non-existent transaction"""
    result = transaction_dal.delete_transaction('999')
    assert result is False