import pytest
import uuid
from prometheus_swarm.utils.transaction_id import validate_transaction_id

def test_valid_transaction_id():
    """Test valid UUID v4 transaction IDs"""
    valid_ids = [
        str(uuid.uuid4()),  # Generating random valid UUIDs
        '550e8400-e29b-41d4-a716-446655440000',
        '123e4567-e89b-42d3-a456-426614174000'
    ]
    for tid in valid_ids:
        assert validate_transaction_id(tid), f"Failed for valid transaction ID: {tid}"

def test_invalid_transaction_id():
    """Test various invalid transaction ID scenarios"""
    invalid_ids = [
        None,               # None value
        '',                 # Empty string
        '   ',              # Whitespace
        'not-a-uuid',       # Completely invalid string
        '123456789',        # Short string
        str(uuid.uuid1()),  # UUID v1 (not v4)
        str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com')),  # UUID v3
        str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com')),  # UUID v5
        '550e8400-e29b-51d4-a716-446655440000',  # Invalid version (5 instead of 4)
        '550e8400-e29b-41d4-c716-446655440000'   # Invalid variant
    ]
    for tid in invalid_ids:
        assert not validate_transaction_id(tid), f"Incorrectly accepted invalid transaction ID: {tid}"

def test_uuid_case_insensitivity():
    """Test that transaction ID validation is case-insensitive"""
    uuid_str = str(uuid.uuid4())
    assert validate_transaction_id(uuid_str.lower())
    assert validate_transaction_id(uuid_str.upper())

def test_transaction_id_format():
    """Test specific transaction ID format constraints"""
    # Verify version 4 characteristics
    test_uuid = str(uuid.uuid4())
    assert test_uuid[14] == '4'  # Version 4 always has '4' in this position
    assert test_uuid[19] in '89ab'  # Variant always starts with 8, 9, a, or b

def test_edge_cases():
    """Test edge cases that might be problematic"""
    edge_cases = [
        # UUIDs with different variations
        '00000000-0000-4000-8000-000000000000',  # Minimum valid UUID v4
        'ffffffff-ffff-4fff-bfff-ffffffffffff',  # Maximum valid UUID v4
    ]
    for tid in edge_cases:
        assert validate_transaction_id(tid), f"Failed for edge case UUID: {tid}"