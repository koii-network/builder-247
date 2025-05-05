import pytest
import uuid
from src.transaction_id_validator import validate_transaction_id

def test_valid_uuid_v1():
    """Test that a valid v1 UUID is accepted"""
    transaction_id = str(uuid.uuid1())
    assert validate_transaction_id(transaction_id) is True

def test_valid_uuid_v3():
    """Test that a valid v3 UUID is accepted"""
    transaction_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com'))
    assert validate_transaction_id(transaction_id) is True

def test_valid_uuid_v4():
    """Test that a valid v4 UUID is accepted"""
    transaction_id = str(uuid.uuid4())
    assert validate_transaction_id(transaction_id) is True

def test_valid_uuid_v5():
    """Test that a valid v5 UUID is accepted"""
    transaction_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com'))
    assert validate_transaction_id(transaction_id) is True

def test_invalid_uuid_v2():
    """Test that a v2 UUID is rejected"""
    # Note: uuid.uuid2() is not implemented in Python
    transaction_id = '12345678-1234-2234-1234-123456789abc'
    assert validate_transaction_id(transaction_id) is False

def test_malformed_uuid():
    """Test that malformed UUIDs are rejected"""
    malformed_uuids = [
        'not-a-uuid',
        '123',
        'g1234567-1234-4567-1234-123456789abc',  # Invalid hex character
        '12345678-1234-4567-1234-123456789abcD'  # Too long
    ]
    for bad_uuid in malformed_uuids:
        assert validate_transaction_id(bad_uuid) is False

def test_empty_string():
    """Test that an empty string is rejected"""
    assert validate_transaction_id('') is False

def test_none_input():
    """Test that None input is rejected"""
    assert validate_transaction_id(None) is False

def test_non_string_input():
    """Test that non-string inputs are rejected"""
    non_string_inputs = [
        42,
        3.14,
        ['uuid'],
        {'uuid': 'value'},
        True,
        False
    ]
    for bad_input in non_string_inputs:
        assert validate_transaction_id(bad_input) is False