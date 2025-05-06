import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_tracking import Base, TransactionAccessLayer, Transaction

@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing"""
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def session(engine):
    """Create a database session with schema"""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def transaction_dal(session):
    """Create a TransactionAccessLayer instance"""
    return TransactionAccessLayer(session)

def test_create_transaction(transaction_dal):
    """Test creating a new transaction"""
    transaction = transaction_dal.create_transaction(
        transaction_type='purchase', 
        amount=100.50, 
        extra_data={'item': 'laptop'}
    )
    
    assert transaction is not None
    assert transaction.transaction_type == 'purchase'
    assert transaction.amount == 100.50
    assert transaction.extra_data == {'item': 'laptop'}
    assert transaction.status == 'pending'
    assert transaction.id is not None

def test_create_transaction_invalid_inputs(transaction_dal):
    """Test creating transactions with invalid inputs"""
    with pytest.raises(ValueError, match="Transaction type cannot be empty"):
        transaction_dal.create_transaction(transaction_type='', amount=100)
    
    with pytest.raises(ValueError, match="Transaction amount must be non-negative"):
        transaction_dal.create_transaction(transaction_type='test', amount=-50)

def test_get_transaction_by_id(transaction_dal):
    """Test retrieving a transaction by ID"""
    transaction = transaction_dal.create_transaction(
        transaction_type='sale', 
        amount=200.75
    )
    
    retrieved_transaction = transaction_dal.get_transaction_by_id(transaction.id)
    
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id
    assert retrieved_transaction.amount == 200.75

def test_get_transaction_by_id_not_found(transaction_dal):
    """Test retrieving a non-existent transaction"""
    retrieved_transaction = transaction_dal.get_transaction_by_id(9999)
    assert retrieved_transaction is None

def test_get_transactions_by_type(transaction_dal):
    """Test retrieving transactions by type"""
    transaction_dal.create_transaction(transaction_type='sale', amount=100)
    transaction_dal.create_transaction(transaction_type='sale', amount=200)
    transaction_dal.create_transaction(transaction_type='purchase', amount=300)
    
    sale_transactions = transaction_dal.get_transactions_by_type('sale')
    
    assert len(sale_transactions) == 2
    assert all(t.transaction_type == 'sale' for t in sale_transactions)

def test_update_transaction_status(transaction_dal):
    """Test updating a transaction's status"""
    transaction = transaction_dal.create_transaction(
        transaction_type='refund', 
        amount=50.25
    )
    
    updated_transaction = transaction_dal.update_transaction_status(
        transaction.id, 
        'completed'
    )
    
    assert updated_transaction is not None
    assert updated_transaction.status == 'completed'

def test_update_transaction_status_invalid_input(transaction_dal):
    """Test updating transaction status with invalid input"""
    transaction = transaction_dal.create_transaction(
        transaction_type='test', 
        amount=100
    )
    
    with pytest.raises(ValueError, match="Transaction status cannot be empty"):
        transaction_dal.update_transaction_status(transaction.id, '')

def test_delete_transaction(transaction_dal):
    """Test deleting a transaction"""
    transaction = transaction_dal.create_transaction(
        transaction_type='deletion_test', 
        amount=75.50
    )
    
    result = transaction_dal.delete_transaction(transaction.id)
    
    assert result is True
    assert transaction_dal.get_transaction_by_id(transaction.id) is None

def test_delete_transaction_not_found(transaction_dal):
    """Test deleting a non-existent transaction"""
    result = transaction_dal.delete_transaction(9999)
    assert result is False