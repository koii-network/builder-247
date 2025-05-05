import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id, generate_transaction_id

def test_validate_transaction_id_valid():
    """Test that a valid v4 UUID passes validation."""
    test_id = str(uuid.uuid4())
    assert validate_transaction_id(test_id) is True

def test_validate_transaction_id_none():
    """Test that None fails validation."""
    assert validate_transaction_id(None) is False

def test_validate_transaction_id_empty_string():
    """Test that an empty string fails validation."""
    assert validate_transaction_id('') is False
    assert validate_transaction_id('   ') is False

def test_validate_transaction_id_invalid_format():
    """Test various invalid transaction ID formats."""
    # Non-UUID format
    assert validate_transaction_id('not-a-uuid') is False
    
    # Different UUID versions
    assert validate_transaction_id(str(uuid.uuid1())) is False
    assert validate_transaction_id(str(uuid.uuid3(uuid.NAMESPACE_DNS, 'test'))) is False
    assert validate_transaction_id(str(uuid.uuid5(uuid.NAMESPACE_DNS, 'test'))) is False

def test_validate_transaction_id_invalid_type():
    """Test that non-string types fail validation."""
    assert validate_transaction_id(123) is False
    assert validate_transaction_id([]) is False
    assert validate_transaction_id({}) is False

def test_generate_transaction_id():
    """Test that generated transaction IDs are valid."""
    transaction_id = generate_transaction_id()
    
    # Check that the generated ID passes validation
    assert validate_transaction_id(transaction_id) is True
    
    # Check that multiple generated IDs are unique
    transaction_id2 = generate_transaction_id()
    assert transaction_id != transaction_id2

def test_transaction_id_uuid_version():
    """Explicitly test that generated IDs are version 4."""
    transaction_id = generate_transaction_id()
    uuid_obj = uuid.UUID(transaction_id)
    
    assert uuid_obj.version == 4