import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prometheus_swarm.database.transaction_models import Base, Transaction, TransactionStatus, TransactionAuditLog
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def engine():
    """Create an in-memory SQLite engine for testing."""
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='module')
def tables(engine):
    """Create tables in the test database."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine, tables):
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_create_transaction(session):
    """Test creating a new transaction."""
    transaction = Transaction(
        transaction_type='payment',
        amount=100.50,
        status=TransactionStatus.PENDING,
        description='Test transaction',
        external_id='EXT001'
    )
    
    session.add(transaction)
    session.commit()
    
    assert transaction.id is not None
    assert transaction.status == TransactionStatus.PENDING
    assert transaction.amount == 100.50
    assert transaction.description == 'Test transaction'
    assert transaction.external_id == 'EXT001'

def test_transaction_audit_log(session):
    """Test creating an audit log for a transaction."""
    transaction = Transaction(
        transaction_type='transfer',
        amount=250.75,
        status=TransactionStatus.COMPLETED
    )
    session.add(transaction)
    session.flush()
    
    audit_log = TransactionAuditLog(
        transaction_id=transaction.id,
        action='CREATE',
        actor='system',
        details='Initial transaction creation'
    )
    session.add(audit_log)
    session.commit()
    
    assert audit_log.id is not None
    assert audit_log.transaction_id == transaction.id
    assert audit_log.action == 'CREATE'
    assert audit_log.actor == 'system'

def test_transaction_status_change(session):
    """Test changing a transaction's status."""
    transaction = Transaction(
        transaction_type='refund',
        amount=50.00,
        status=TransactionStatus.PENDING
    )
    session.add(transaction)
    session.flush()
    
    # Change status and log the action
    transaction.status = TransactionStatus.COMPLETED
    session.commit()
    
    audit_log = TransactionAuditLog(
        transaction_id=transaction.id,
        action='STATUS_UPDATE',
        actor='admin',
        details='Changed status from PENDING to COMPLETED'
    )
    session.add(audit_log)
    session.commit()
    
    assert transaction.status == TransactionStatus.COMPLETED
    assert len(transaction.audit_logs) == 1
    assert transaction.audit_logs[0].action == 'STATUS_UPDATE'

def test_unique_external_id_constraint(session):
    """Test that external_id is unique."""
    transaction1 = Transaction(
        transaction_type='payment',
        amount=100.00,
        external_id='UNIQUE001'
    )
    session.add(transaction1)
    session.commit()
    
    with pytest.raises(Exception):  # SQLAlchemy will raise an IntegrityError
        transaction2 = Transaction(
            transaction_type='payment',
            amount=200.00,
            external_id='UNIQUE001'
        )
        session.add(transaction2)
        session.commit()

def test_transaction_timestamp(session):
    """Test transaction timestamp behavior."""
    transaction = Transaction(
        transaction_type='reward',
        amount=25.00
    )
    session.add(transaction)
    session.commit()
    
    assert transaction.timestamp is not None
    assert isinstance(transaction.timestamp, datetime)
    assert transaction.timestamp <= datetime.utcnow()
    assert transaction.timestamp > datetime.utcnow() - timedelta(seconds=1)