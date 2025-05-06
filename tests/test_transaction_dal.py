import pytest
from datetime import datetime, timedelta
from src.transaction_dal import TransactionDataAccessLayer, Transaction

def test_create_transaction():
    dal = TransactionDataAccessLayer()
    transaction = dal.create_transaction(100.50, "Test Transaction", "groceries")
    
    assert transaction.id is not None
    assert transaction.amount == 100.50
    assert transaction.description == "Test Transaction"
    assert transaction.category == "groceries"
    assert transaction.status == "pending"
    assert isinstance(transaction.timestamp, datetime)

def test_create_transaction_invalid_amount():
    dal = TransactionDataAccessLayer()
    
    with pytest.raises(ValueError, match="Transaction amount must be positive"):
        dal.create_transaction(-50, "Invalid Transaction")

def test_get_transaction():
    dal = TransactionDataAccessLayer()
    transaction = dal.create_transaction(200, "Get Transaction Test")
    
    retrieved_transaction = dal.get_transaction(transaction.id)
    
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id
    assert retrieved_transaction.amount == 200
    assert retrieved_transaction.description == "Get Transaction Test"

def test_get_nonexistent_transaction():
    dal = TransactionDataAccessLayer()
    
    assert dal.get_transaction("non_existent_id") is None

def test_update_transaction():
    dal = TransactionDataAccessLayer()
    transaction = dal.create_transaction(300, "Update Transaction")
    
    updated_transaction = dal.update_transaction(
        transaction.id, 
        amount=350, 
        description="Updated Description", 
        category="entertainment",
        status="completed"
    )
    
    assert updated_transaction is not None
    assert updated_transaction.amount == 350
    assert updated_transaction.description == "Updated Description"
    assert updated_transaction.category == "entertainment"
    assert updated_transaction.status == "completed"

def test_update_transaction_invalid_amount():
    dal = TransactionDataAccessLayer()
    transaction = dal.create_transaction(300, "Update Transaction")
    
    with pytest.raises(ValueError, match="Transaction amount must be positive"):
        dal.update_transaction(transaction.id, amount=-50)

def test_update_nonexistent_transaction():
    dal = TransactionDataAccessLayer()
    
    assert dal.update_transaction("non_existent_id", amount=500) is None

def test_delete_transaction():
    dal = TransactionDataAccessLayer()
    transaction = dal.create_transaction(400, "Delete Transaction")
    
    assert dal.delete_transaction(transaction.id) is True
    assert dal.get_transaction(transaction.id) is None

def test_delete_nonexistent_transaction():
    dal = TransactionDataAccessLayer()
    
    assert dal.delete_transaction("non_existent_id") is False

def test_list_transactions():
    dal = TransactionDataAccessLayer()
    
    # Create some test transactions
    t1 = dal.create_transaction(100, "Groceries", "food")
    t2 = dal.create_transaction(200, "Movie", "entertainment")
    t3 = dal.create_transaction(300, "Utilities", "bills")
    dal.update_transaction(t3.id, status="completed")
    
    # Test listing all transactions
    all_transactions = dal.list_transactions()
    assert len(all_transactions) == 3
    
    # Test filtering by category
    food_transactions = dal.list_transactions(category="food")
    assert len(food_transactions) == 1
    assert food_transactions[0].id == t1.id
    
    # Test filtering by status
    completed_transactions = dal.list_transactions(status="completed")
    assert len(completed_transactions) == 1
    assert completed_transactions[0].id == t3.id
    
    # Test combined filtering
    filtered_transactions = dal.list_transactions(category="food", status="pending")
    assert len(filtered_transactions) == 1
    assert filtered_transactions[0].id == t1.id