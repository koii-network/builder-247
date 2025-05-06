import pytest
from prometheus_swarm.tools.transaction_id_checker import (
    check_transaction_id_duplicates, 
    validate_transaction_ids, 
    TransactionIDDuplicateError
)

def test_check_transaction_id_duplicates_no_duplicates():
    """Test that no duplicates are returned when there are none."""
    transaction_ids = ['123', '456', '789']
    assert check_transaction_id_duplicates(transaction_ids) == []

def test_check_transaction_id_duplicates_with_duplicates():
    """Test that duplicates are correctly identified."""
    transaction_ids = ['123', '456', '789', '123', '456']
    assert set(check_transaction_id_duplicates(transaction_ids)) == {'123', '456'}

def test_validate_transaction_ids_no_duplicates():
    """Test validation passes when no duplicates exist."""
    transaction_ids = ['123', '456', '789']
    validate_transaction_ids(transaction_ids)  # Should not raise an exception

def test_validate_transaction_ids_raises_on_duplicates():
    """Test that validation raises an exception when duplicates exist."""
    transaction_ids = ['123', '456', '789', '123']
    with pytest.raises(TransactionIDDuplicateError) as excinfo:
        validate_transaction_ids(transaction_ids)
    
    assert '123' in str(excinfo.value)

def test_check_transaction_id_duplicates_invalid_input_type():
    """Test that TypeError is raised for non-list input."""
    with pytest.raises(TypeError):
        check_transaction_id_duplicates("not a list")

def test_check_transaction_id_duplicates_non_string_input():
    """Test that TypeError is raised for non-string list inputs."""
    with pytest.raises(TypeError):
        check_transaction_id_duplicates(['123', 456, '789'])

def test_check_transaction_id_duplicates_empty_string():
    """Test that ValueError is raised for empty string inputs."""
    with pytest.raises(ValueError):
        check_transaction_id_duplicates(['123', '', '789'])

def test_validate_transaction_ids_empty_list():
    """Test validation works correctly with an empty list."""
    validate_transaction_ids([])  # Should not raise an exception

def test_check_transaction_id_duplicates_case_sensitive():
    """Test that duplicate checks are case-sensitive."""
    transaction_ids = ['123', '123', 'ABC', 'abc']
    assert set(check_transaction_id_duplicates(transaction_ids)) == {'123'}
    assert len(check_transaction_id_duplicates(transaction_ids)) == 1