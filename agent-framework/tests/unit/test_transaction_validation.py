"""
Unit tests for transaction ID validation.

This module tests the transaction_validation utility functions.
"""

import pytest
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id


def test_valid_transaction_id():
    """Test that a valid UUID v4 passes validation."""
    valid_uuid = str(uuid.uuid4())
    assert validate_transaction_id(valid_uuid) is True


def test_invalid_transaction_ids():
    """Test various invalid transaction ID formats."""
    invalid_cases = [
        None,               # None value
        "",                 # Empty string
        "not-a-uuid",       # Random string
        "12345",            # Too short
        str(uuid.uuid1()),  # UUID v1 (not v4)
        "f47ac10b-58cc-4372-a567-0e02b2c3d479".replace('4', '5')  # Invalid version
    ]

    for case in invalid_cases:
        assert validate_transaction_id(case) is False, f"Failed for input: {case}"


def test_uuid_version_constraint():
    """Ensure only UUID v4 is accepted."""
    v1_uuid = str(uuid.uuid1())
    v3_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org'))
    v4_uuid = str(uuid.uuid4())
    v5_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org'))

    assert validate_transaction_id(v1_uuid) is False
    assert validate_transaction_id(v3_uuid) is False
    assert validate_transaction_id(v4_uuid) is True
    assert validate_transaction_id(v5_uuid) is False


def test_uuid_format_constraints():
    """Test various UUID formatting constraints."""
    test_cases = [
        '123e4567-e89b-4000-a456-426614174000',  # Correct v4 format
        '123E4567-E89B-4000-A456-426614174000',  # Uppercase
        '123e4567-e89b-4000-a456-426614174000',  # Lowercase
    ]

    for case in test_cases:
        assert validate_transaction_id(case) is True, f"Failed for input: {case}"

    malformed_cases = [
        '123e4567-e89b-5000-a456-426614174000',  # Invalid version
        '123e4567-e89b-4000-c456-426614174000',  # Invalid variant
        '123e4567-e89b-4000-a456426614174000',   # Missing hyphen
    ]

    for case in malformed_cases:
        assert validate_transaction_id(case) is False, f"Failed for input: {case}"