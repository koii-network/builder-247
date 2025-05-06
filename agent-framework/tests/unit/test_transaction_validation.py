import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that a valid version 4 UUID passes validation."""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_types():
    """Test various invalid input types."""
    invalid_inputs = [
        None,
        123,
        [],
        {},
        "",
        "   ",
        b"some_bytes"
    ]
    
    for invalid_input in invalid_inputs:
        assert validate_transaction_id(invalid_input) is False, f"Failed for input: {invalid_input}"

def test_invalid_uuid_formats():
    """Test various invalid UUID formats."""
    invalid_uuids = [
        "not-a-uuid",
        "123e4567-e89b-12d3-a456-426614174000",  # malformed UUID
        str(uuid.uuid1()),  # version 1 UUID
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')),  # version 3 UUID
        str(uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org'))   # version 5 UUID
    ]
    
    for invalid_uuid in invalid_uuids:
        assert validate_transaction_id(invalid_uuid) is False, f"Failed for UUID: {invalid_uuid}"

def test_whitespace_transaction_id():
    """Test that whitespace-only transaction IDs are invalid."""
    whitespace_ids = [
        " ",
        "\t",
        "\n",
        "   \t\n"
    ]
    
    for whitespace_id in whitespace_ids:
        assert validate_transaction_id(whitespace_id) is False, f"Failed for whitespace ID: {whitespace_id}"

def test_edge_case_uuids():
    """Test edge case UUIDs that might slip through validation."""
    edge_cases = [
        "00000000-0000-4000-8000-000000000000",  # Minimal valid v4 UUID
        "ffffffff-ffff-4fff-bfff-ffffffffffff"   # Maximal valid v4 UUID
    ]
    
    for edge_uuid in edge_cases:
        assert validate_transaction_id(edge_uuid) is True, f"Failed for edge UUID: {edge_uuid}"