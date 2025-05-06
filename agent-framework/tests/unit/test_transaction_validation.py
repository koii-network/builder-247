"""
Unit tests for transaction ID validation utility.
"""
import pytest
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_valid_transaction_id():
    """Test valid transaction ID scenarios."""
    valid_ids = [
        '123e4567-e89b-12d3-a456-426614174000',  # Standard UUID v4
        '550e8400-e29b-41d4-a716-446655440000',  # Another valid UUID
        '11111111-1111-1111-1111-111111111111'   # All 1's
    ]
    for valid_id in valid_ids:
        assert validate_transaction_id(valid_id) is True, f"Failed for valid ID: {valid_id}"

def test_invalid_transaction_ids():
    """Test various invalid transaction ID scenarios."""
    invalid_ids = [
        '',                 # Empty string
        '   ',              # Whitespace
        None,               # None value
        123,                # Integer
        'invalid-uuid',     # Invalid format
        '123e4567-e89b-12d3-a456-42661417400',   # Too short
        '123e4567-e89b-12d3-a456-4266141740000', # Too long
        '123g4567-e89b-12d3-a456-426614174000',  # Invalid hex character
        '550e8400-e29b-41d4-a716-44665544000Z',  # Invalid character at end
    ]
    for invalid_id in invalid_ids:
        assert validate_transaction_id(invalid_id) is False, f"Failed to catch invalid ID: {invalid_id}"

def test_case_insensitivity():
    """Test that UUID validation is case-insensitive."""
    mixed_case_ids = [
        '123E4567-E89B-12D3-A456-426614174000',  # Uppercase
        '123e4567-E89b-12D3-a456-426614174000'   # Mixed case
    ]
    for mixed_case_id in mixed_case_ids:
        assert validate_transaction_id(mixed_case_id) is True, f"Failed case-insensitive test: {mixed_case_id}"

def test_whitespace_stripping():
    """Test that leading/trailing whitespace is handled correctly."""
    whitespace_ids = [
        '  123e4567-e89b-12d3-a456-426614174000  ',
        '\t123e4567-e89b-12d3-a456-426614174000\n'
    ]
    for whitespace_id in whitespace_ids:
        assert validate_transaction_id(whitespace_id) is True, f"Failed whitespace test: {whitespace_id}"