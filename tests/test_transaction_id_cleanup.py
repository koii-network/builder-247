import pytest
from src.transaction_id_cleanup import TransactionIDCleanup

class TestTransactionIDCleanup:
    def test_clean_transaction_id_string(self):
        """Test cleaning a transaction ID from a string."""
        assert TransactionIDCleanup.clean_transaction_id("  Transaction-123  ") == "transaction-123"
    
    def test_clean_transaction_id_integer(self):
        """Test cleaning a transaction ID from an integer."""
        assert TransactionIDCleanup.clean_transaction_id(12345) == "12345"
    
    def test_clean_transaction_id_none(self):
        """Test handling None input."""
        assert TransactionIDCleanup.clean_transaction_id(None) is None
    
    def test_clean_transaction_id_special_chars(self):
        """Test removing special characters."""
        assert TransactionIDCleanup.clean_transaction_id("TXN#@123!ABC") == "txn123abc"
    
    def test_clean_transaction_id_invalid_type(self):
        """Test raising TypeError for invalid input types."""
        with pytest.raises(TypeError):
            TransactionIDCleanup.clean_transaction_id({"key": "value"})
    
    def test_validate_transaction_id_valid(self):
        """Test validating a valid transaction ID."""
        assert TransactionIDCleanup.validate_transaction_id("transaction-123") is True
    
    def test_validate_transaction_id_none(self):
        """Test validation of None input."""
        assert TransactionIDCleanup.validate_transaction_id(None) is False
    
    def test_validate_transaction_id_too_short(self):
        """Test validation of transaction ID that is too short."""
        assert TransactionIDCleanup.validate_transaction_id("1234") is False
    
    def test_validate_transaction_id_too_long(self):
        """Test validation of transaction ID that is too long."""
        long_id = "a" * 51
        assert TransactionIDCleanup.validate_transaction_id(long_id) is False
    
    def test_validate_transaction_id_invalid_chars(self):
        """Test validation of transaction ID with invalid characters."""
        assert TransactionIDCleanup.validate_transaction_id("transaction 123") is False
    
    def test_custom_length_validation(self):
        """Test validation with custom length constraints."""
        # Custom min and max length
        assert TransactionIDCleanup.validate_transaction_id("txn", min_length=2, max_length=3) is True
        assert TransactionIDCleanup.validate_transaction_id("txn", min_length=4, max_length=5) is False