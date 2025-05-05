import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that valid UUIDs are correctly validated."""
    valid_uuids = [
        str(uuid.uuid4()),
        str(uuid.uuid4()).upper(),
        str(uuid.uuid4()).lower()
    ]
    
    for transaction_id in valid_uuids:
        assert validate_transaction_id(transaction_id) is True, f"Failed for {transaction_id}"

def test_invalid_transaction_id():
    """Test various invalid transaction ID scenarios."""
    invalid_cases = [
        None,                    # None value
        "",                      # Empty string
        "   ",                   # Whitespace
        "not-a-uuid",            # Incorrect format
        "12345678-1234-1234-1234-123456789012",  # Invalid UUID
        "z0000000-0000-4000-b000-000000000000",  # Invalid characters
        str(uuid.uuid1()),       # UUID v1 (not v4)
        str(uuid.uuid3(uuid.NAMESPACE_DNS, "test")),  # UUID v3
        str(uuid.uuid5(uuid.NAMESPACE_DNS, "test"))   # UUID v5
    ]
    
    for invalid_id in invalid_cases:
        assert validate_transaction_id(invalid_id) is False, f"Failed for {invalid_id}"

def test_edge_cases():
    """Test edge cases for transaction ID validation."""
    edge_cases = [
        "00000000-0000-4000-b000-000000000000",  # All zeros except version
        "ffffffff-ffff-4fff-bfff-ffffffffffff",  # All max hex values
        " " + str(uuid.uuid4()) + " ",           # Whitespace padded UUID
    ]
    
    for edge_case in edge_cases:
        # Strip whitespace and validate
        assert validate_transaction_id(edge_case.strip()) is True, f"Failed for {edge_case}"
        
        # Non-stripped case should be False
        if edge_case.strip() != edge_case:
            assert validate_transaction_id(edge_case) is False, f"Failed for {edge_case}"