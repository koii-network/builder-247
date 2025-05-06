import pytest
import os
import tempfile
from datetime import datetime, timedelta
from prometheus_swarm.database.transaction_tracking import TransactionTracker

class TestTransactionTracker:
    @pytest.fixture
    def transaction_tracker(self):
        """Create a transaction tracker with a temporary database."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        # Override db path for the test
        tracker = TransactionTracker(temp_db_path)
        yield tracker
        
        # Clean up the temporary database
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
    
    def test_record_transaction(self, transaction_tracker):
        """Test recording a valid transaction."""
        transaction_id = transaction_tracker.record_transaction(
            transaction_type='deposit',
            description='Test deposit',
            amount=100.50
        )
        
        assert transaction_id is not None
        assert isinstance(transaction_id, int)
    
    def test_record_transaction_invalid_params(self, transaction_tracker):
        """Test recording a transaction with invalid parameters."""
        with pytest.raises(ValueError):
            transaction_tracker.record_transaction(
                transaction_type='',
                description='Invalid transaction',
                amount=-50
            )
    
    def test_get_transactions(self, transaction_tracker):
        """Test retrieving transactions."""
        # Record some test transactions
        transaction_tracker.record_transaction('deposit', 'Test 1', 100)
        transaction_tracker.record_transaction('withdrawal', 'Test 2', 50)
        
        transactions = transaction_tracker.get_transactions()
        
        assert len(transactions) == 2
        assert all('id' in t and 'transaction_type' in t for t in transactions)
    
    def test_get_transactions_with_filters(self, transaction_tracker):
        """Test retrieving transactions with various filters."""
        now = datetime.now()
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)
        
        transaction_tracker.record_transaction('deposit', 'Deposit 1', 100)
        transaction_tracker.record_transaction('withdrawal', 'Withdrawal', 50)
        
        # Filter by transaction type
        type_filtered = transaction_tracker.get_transactions(transaction_type='deposit')
        assert len(type_filtered) == 1
        assert type_filtered[0]['transaction_type'] == 'deposit'
        
        # Filter by date range
        date_filtered = transaction_tracker.get_transactions(start_date=past, end_date=future)
        assert len(date_filtered) == 2
    
    def test_get_total_amount(self, transaction_tracker):
        """Test calculating total transaction amount."""
        # Track transactions in a specific test setup
        transaction_tracker.record_transaction('deposit', 'Deposit 1', 100)
        transaction_tracker.record_transaction('deposit', 'Deposit 2', 200)
        transaction_tracker.record_transaction('withdrawal', 'Withdrawal', 50)
        
        print("Transactions:", transaction_tracker.get_transactions())
        
        # Total amount for all transactions
        total = transaction_tracker.get_total_amount()
        print("Total amount:", total)
        assert total == 250
        
        # Total amount for deposits only
        deposit_total = transaction_tracker.get_total_amount(transaction_type='deposit')
        print("Deposit total:", deposit_total)
        assert deposit_total == 300
    
    def test_transaction_metadata(self, transaction_tracker):
        """Test recording and retrieving transaction metadata."""
        metadata = {'source': 'test', 'category': 'income'}
        transaction_id = transaction_tracker.record_transaction(
            transaction_type='deposit',
            description='Metadata test',
            amount=75.25,
            metadata=metadata
        )
        
        transactions = transaction_tracker.get_transactions()
        matching_transaction = next(
            (t for t in transactions if t['id'] == transaction_id), 
            None
        )
        
        assert matching_transaction is not None
        assert str(metadata) in str(matching_transaction)