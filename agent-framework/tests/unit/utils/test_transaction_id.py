import uuid
import pytest
from prometheus_swarm.utils.transaction_id import cleanup_transaction_id

def test_cleanup_transaction_id_valid_uuid():
    """Test cleaning up a valid UUID."""
    test_uuid = uuid.uuid4()
    result = cleanup_transaction_id(test_uuid)
    assert result == str(test_uuid)

def test_cleanup_transaction_id_valid_string_uuid():
    """Test cleaning up a valid UUID string."""
    test_uuid_str = str(uuid.uuid4())
    result = cleanup_transaction_id(test_uuid_str)
    assert result == test_uuid_str

def test_cleanup_transaction_id_with_whitespace():
    """Test cleaning up a UUID string with whitespace."""
    test_uuid_str = f"  {str(uuid.uuid4())}  "
    result = cleanup_transaction_id(test_uuid_str)
    assert result == test_uuid_str.strip()

def test_cleanup_transaction_id_with_extra_characters():
    """Test cleaning up a UUID string with extra characters."""
    base_uuid = str(uuid.uuid4())
    test_uuid_str = f"uuid:{base_uuid}:extra"
    result = cleanup_transaction_id(test_uuid_str)
    assert result == base_uuid

def test_cleanup_transaction_id_invalid():
    """Test that an invalid UUID returns None."""
    invalid_uuid_str = "not-a-valid-uuid"
    result = cleanup_transaction_id(invalid_uuid_str)
    assert result is None

def test_cleanup_transaction_id_type_error():
    """Test that a non-string, non-UUID input raises a TypeError."""
    with pytest.raises(TypeError):
        cleanup_transaction_id(12345)