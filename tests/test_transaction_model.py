import pytest
from datetime import datetime
from src.models.transaction import Transaction, TransactionType

def test_transaction_creation():
    """Test creating a basic transaction."""
    transaction = Transaction(
        amount=100.50,
        transaction_type=TransactionType.DEPOSIT,
        description="Test deposit",
        source_account="SRC123",
        destination_account="DST456",
        timestamp=datetime.now()  # Explicitly set timestamp
    )
    
    assert transaction.amount == 100.50
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.description == "Test deposit"
    assert transaction.source_account == "SRC123"
    assert transaction.destination_account == "DST456"
    assert transaction.status == "completed"
    assert isinstance(transaction.timestamp, datetime)

def test_transaction_repr():
    """Test the string representation of a transaction."""
    transaction = Transaction(
        amount=200.75,
        transaction_type=TransactionType.WITHDRAWAL,
        source_account="SRC789",
        timestamp=datetime.now()
    )
    
    repr_str = repr(transaction)
    assert "Transaction" in repr_str
    assert "amount=200.75" in repr_str
    assert "type=withdrawal" in repr_str

def test_transaction_validation():
    """Test transaction validation rules."""
    # Valid deposit
    valid_deposit = Transaction(
        amount=50.00,
        transaction_type=TransactionType.DEPOSIT,
        destination_account="DST123",
        timestamp=datetime.now()
    )
    assert valid_deposit.validate() is True

    # Invalid negative amount
    invalid_amount = Transaction(
        amount=-50.00,
        transaction_type=TransactionType.WITHDRAWAL,
        source_account="SRC456",
        timestamp=datetime.now()
    )
    assert invalid_amount.validate() is False

    # Transfer without source account
    invalid_transfer = Transaction(
        amount=100.00,
        transaction_type=TransactionType.TRANSFER,
        destination_account="DST789",
        timestamp=datetime.now()
    )
    assert invalid_transfer.validate() is False

    # Withdrawal without source account
    invalid_withdrawal = Transaction(
        amount=75.00,
        transaction_type=TransactionType.WITHDRAWAL,
        timestamp=datetime.now()
    )
    assert invalid_withdrawal.validate() is False

def test_transaction_types():
    """Test different transaction types."""
    transaction_types = [
        TransactionType.DEPOSIT,
        TransactionType.WITHDRAWAL,
        TransactionType.TRANSFER,
        TransactionType.PURCHASE,
        TransactionType.REFUND
    ]
    
    for tx_type in transaction_types:
        transaction = Transaction(
            amount=50.00,
            transaction_type=tx_type,
            source_account="SRC000",
            destination_account="DST000",
            timestamp=datetime.now()
        )
        assert transaction.transaction_type == tx_type

def test_transaction_enum_values():
    """Test transaction type enum values."""
    assert TransactionType.DEPOSIT.value == 'deposit'
    assert TransactionType.WITHDRAWAL.value == 'withdrawal'
    assert TransactionType.TRANSFER.value == 'transfer'
    assert TransactionType.PURCHASE.value == 'purchase'
    assert TransactionType.REFUND.value == 'refund'