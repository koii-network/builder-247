"""Tests for transaction ID validation."""

import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test that valid UUIDs pass validation."""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_formats():
    """Test various invalid transaction ID formats."""
    invalid_ids = [
        None,               # None
        "",                 # Empty string
        "not-a-uuid",       # Random string
        "123-456-789",      # Malformed UUID
        123,                # Integer
        ["uuid"],           # List
        {"id": "uuid"}      # Dictionary
    ]
    
    for invalid_id in invalid_ids:
        assert validate_transaction_id(invalid_id) is False

def test_different_uuid_versions():
    """Test UUIDs of different versions."""
    uuid_versions = [
        uuid.uuid1(),   # Time-based
        uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com'),  # Namespace-based
        uuid.uuid4(),   # Random
        uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com')   # Name-based
    ]
    
    for version in uuid_versions:
        assert validate_transaction_id(str(version)) is True