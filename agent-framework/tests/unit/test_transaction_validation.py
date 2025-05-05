import pytest
import uuid
from prometheus_swarm.utils.transaction import validate_transaction_id

def test_valid_transaction_id():
    """Test that valid UUIDs are accepted"""
    valid_ids = [
        str(uuid.uuid4()),  # Standard UUID
        str(uuid.uuid1()),  # Time-based UUID
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com')),  # Name-based UUID
        str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com'))   # Name-based UUID
    ]
    
    for transaction_id in valid_ids:
        assert validate_transaction_id(transaction_id) is True, f"Failed for {transaction_id}"

def test_invalid_transaction_id():
    """Test that invalid transaction IDs are rejected"""
    invalid_ids = [
        None,               # None value
        "",                 # Empty string
        "   ",              # Whitespace
        "not-a-uuid",       # Random string
        "12345",            # Invalid numeric string
        "g" * 36,           # Invalid characters
        str(uuid.uuid4())[:-1],  # Truncated UUID
        str(uuid.uuid4()) + "extra"  # Extended UUID
    ]
    
    for transaction_id in invalid_ids:
        assert validate_transaction_id(transaction_id) is False, f"Failed to reject {transaction_id}"

def test_transaction_id_properties():
    """Test specific properties of transaction ID validation"""
    # Test with a fresh UUID
    test_id = str(uuid.uuid4())
    assert validate_transaction_id(test_id) is True

    # Test case sensitivity (UUIDs are case-insensitive)
    test_id_upper = test_id.upper()
    assert validate_transaction_id(test_id_upper) is True

    # Test with different UUID versions
    v1_id = str(uuid.uuid1())
    v3_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com'))
    v4_id = str(uuid.uuid4())
    v5_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com'))

    for uid in [v1_id, v3_id, v4_id, v5_id]:
        assert validate_transaction_id(uid) is True