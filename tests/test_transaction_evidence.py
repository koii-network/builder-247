import pytest
from datetime import datetime, timedelta, timezone
import uuid
import json
from src.transaction_evidence import TransactionEvidence

def test_transaction_evidence_creation():
    """Test basic transaction evidence creation."""
    evidence = TransactionEvidence(data={'amount': 100})
    assert evidence.transaction_id is not None
    assert evidence.timestamp is not None
    assert evidence.data == {'amount': 100}
    assert evidence.validate()

def test_transaction_evidence_unique_hash():
    """Ensure each transaction evidence generates a unique hash."""
    evidence1 = TransactionEvidence(data={'amount': 100})
    evidence2 = TransactionEvidence(data={'amount': 100})
    
    assert evidence1.evidence_hash != evidence2.evidence_hash
    assert evidence1.transaction_id != evidence2.transaction_id

def test_transaction_evidence_validation():
    """Test comprehensive validation checks."""
    # Valid evidence
    valid_evidence = TransactionEvidence(data={'amount': 100})
    assert valid_evidence.validate() is True
    
    # Evidence with future timestamp
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(TypeError):
        TransactionEvidence(timestamp=future_time)

def test_transaction_evidence_to_dict():
    """Test conversion of transaction evidence to dictionary."""
    original_data = {'amount': 100, 'description': 'Test Transaction'}
    metadata = {'source': 'test'}
    
    evidence = TransactionEvidence(data=original_data, metadata=metadata)
    evidence_dict = evidence.to_dict()
    
    assert 'transaction_id' in evidence_dict
    assert 'timestamp' in evidence_dict
    assert 'data' in evidence_dict
    assert 'metadata' in evidence_dict
    assert 'evidence_hash' in evidence_dict
    
    assert evidence_dict['data'] == original_data
    assert evidence_dict['metadata'] == metadata

def test_transaction_evidence_from_dict():
    """Test creating transaction evidence from a dictionary."""
    original_dict = {
        'transaction_id': str(uuid.uuid4()),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': {'amount': 200},
        'metadata': {'source': 'test_recreation'}
    }
    
    evidence = TransactionEvidence.from_dict(original_dict)
    
    assert evidence.transaction_id == original_dict['transaction_id']
    assert evidence.data == original_dict['data']
    assert evidence.metadata == original_dict['metadata']
    assert evidence.validate()

def test_transaction_evidence_empty_data():
    """Test creating transaction evidence with empty data."""
    evidence = TransactionEvidence()
    assert evidence.validate()
    assert evidence.data == {}
    assert evidence.metadata == {}

def test_transaction_evidence_complex_data():
    """Test transaction evidence with complex nested data."""
    complex_data = {
        'user': {
            'id': '12345',
            'name': 'John Doe'
        },
        'transaction': {
            'type': 'purchase',
            'amount': 99.99
        }
    }
    
    evidence = TransactionEvidence(data=complex_data)
    assert evidence.validate()
    assert evidence.data == complex_data