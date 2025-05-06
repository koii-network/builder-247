import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import Base, Transaction, TransactionType, TransactionStatus, create_transaction

@pytest.fixture(scope='function')
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='function')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    connection.close()

def test_create_transaction(session):
    """Test creating a basic transaction"""
    transaction = create_transaction(
        session, 
        transaction_type=TransactionType.DEPOSIT, 
        amount=100.50, 
        currency='USD'
    )
    
    assert transaction.id is not None
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.amount == 100.50
    assert transaction.currency == 'USD'
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.reference_code is not None

def test_transaction_representation(session):
    """Test the __repr__ method of Transaction"""
    transaction = create_transaction(
        session, 
        transaction_type=TransactionType.WITHDRAWAL, 
        amount=50.25, 
        currency='EUR'
    )
    
    repr_str = repr(transaction)
    assert 'Transaction' in repr_str
    assert str(transaction.id) in repr_str
    assert str(transaction.transaction_type) in repr_str
    assert str(transaction.amount) in repr_str
    assert str(transaction.status) in repr_str

def test_different_transaction_types(session):
    """Test creating transactions of different types"""
    deposit = create_transaction(
        session, 
        transaction_type=TransactionType.DEPOSIT, 
        amount=100, 
        currency='USD'
    )
    
    withdrawal = create_transaction(
        session, 
        transaction_type=TransactionType.WITHDRAWAL, 
        amount=50, 
        currency='EUR'
    )
    
    transfer = create_transaction(
        session, 
        transaction_type=TransactionType.TRANSFER, 
        amount=75, 
        currency='GBP'
    )
    
    reward = create_transaction(
        session, 
        transaction_type=TransactionType.REWARD, 
        amount=10, 
        currency='USD'
    )
    
    assert deposit.transaction_type == TransactionType.DEPOSIT
    assert withdrawal.transaction_type == TransactionType.WITHDRAWAL
    assert transfer.transaction_type == TransactionType.TRANSFER
    assert reward.transaction_type == TransactionType.REWARD