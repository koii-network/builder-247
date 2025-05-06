import pytest
import uuid
from prometheus_swarm.utils.transaction_id import validate_transaction_id

def test_valid_transaction_id():
    """Test that a valid UUID is recognized as a valid transaction ID."""
    valid_id = str(uuid.uuid4())
    assert validate_transaction_id(valid_id) is True

def test_invalid_transaction_id_types():
    """Test that invalid types are not accepted."""
    invalid_types = [
        None,
        123,
        ['not-a-string'],
        {},
        True,
        False
    ]
    for invalid_type in invalid_types:
        assert validate_transaction_id(invalid_type) is False

def test_empty_transaction_id():
    """Test that empty strings are not valid."""
    empty_ids = [
        '',
        '   ',
        '\t',
        '\n'
    ]
    for empty_id in empty_ids:
        assert validate_transaction_id(empty_id) is False

def test_whitespace_transaction_id():
    """Test that transaction IDs with whitespace are invalid."""
    whitespace_ids = [
        'uuid with space',
        ' uuid',
        'uuid ',
        'uuid\twith\ttab',
        'uuid\nwith\nnewline'
    ]
    for whitespace_id in whitespace_ids:
        assert validate_transaction_id(whitespace_id) is False

def test_invalid_uuid_format():
    """Test that malformed UUIDs are not valid."""
    invalid_uuids = [
        'not-a-uuid',
        'g-uuid-format',
        '12345',
        'ffffffff-ffff-ffff-ffff-ffffffffffff',
        str(uuid.uuid4())[:-1] + 'g',  # Malformed last character
        # Test edge cases with problematic sections
        'ffffffff-ffff-ffff-ffff-ffffffffxx',  # x is not hex
        'ffffffff-ffff-ffff-ffff-ffffffffffff0',  # extra character
        'ffffffff-ffff-ffff-ffff-ffffffffffff-',  # additional segment
        '12345678-1234-1234-1234-123456789012',  # All numeric
        'GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG'  # Non-hex uppercase
    ]
    for invalid_uuid in invalid_uuids:
        assert validate_transaction_id(invalid_uuid) is False