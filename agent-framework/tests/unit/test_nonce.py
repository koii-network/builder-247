import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from prometheus_swarm.database.nonce import Nonce
from prometheus_swarm.database.nonce_storage import InMemoryNonceStorage

def test_nonce_creation():
    """Test basic nonce creation with default parameters."""
    nonce = Nonce()
    assert nonce.id is not None
    assert nonce.value is not None
    assert not nonce.is_expired()
    assert not nonce.used

def test_nonce_custom_value():
    """Test nonce creation with a custom value."""
    custom_value = "test_custom_nonce"
    nonce = Nonce(value=custom_value)
    assert nonce.value == custom_value

def test_nonce_metadata():
    """Test nonce creation with metadata."""
    metadata = {"test_key": "test_value"}
    nonce = Nonce(metadata=metadata)
    assert nonce.metadata == metadata

def test_nonce_expiration():
    """Test nonce expiration."""
    short_lived_nonce = Nonce(expires_in=1)
    assert not short_lived_nonce.is_expired()

    # This will wait just over 1 second
    import time
    time.sleep(1.1)
    assert short_lived_nonce.is_expired()

def test_nonce_mark_as_used():
    """Test marking a nonce as used."""
    nonce = Nonce()
    assert not nonce.used
    nonce.mark_as_used()
    assert nonce.used

def test_nonce_to_dict():
    """Test conversion of nonce to dictionary."""
    nonce = Nonce(metadata={"test": "data"})
    nonce_dict = nonce.to_dict()

    assert isinstance(nonce_dict, dict)
    assert 'id' in nonce_dict
    assert 'value' in nonce_dict
    assert 'created_at' in nonce_dict
    assert 'expires_at' in nonce_dict
    assert 'used' in nonce_dict
    assert 'metadata' in nonce_dict
    assert nonce_dict['metadata'] == {"test": "data"}

def test_nonce_from_dict():
    """Test recreation of nonce from dictionary."""
    nonce_dict = {
        'id': 'test_id',
        'value': 'test_value',
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        'used': False,
        'metadata': {"test": "data"}
    }
    
    nonce = Nonce.from_dict(nonce_dict)
    
    assert nonce.id == 'test_id'
    assert nonce.value == 'test_value'
    assert nonce.metadata == {"test": "data"}
    assert not nonce.used

def test_in_memory_nonce_storage():
    """Test InMemoryNonceStorage functionality."""
    storage = InMemoryNonceStorage()
    nonce = Nonce()

    # Test storing a nonce
    storage.store_nonce(nonce)
    assert storage.get_nonce(nonce.value) is not None

    # Test duplicate nonce storing raises error
    with pytest.raises(ValueError):
        storage.store_nonce(nonce)

    # Test nonce validation
    assert storage.validate_nonce(nonce.value)

    # Test marking nonce as used
    storage.mark_nonce_as_used(nonce.value)
    assert not storage.validate_nonce(nonce.value)

def test_in_memory_nonce_storage_cleanup():
    """Test cleanup of expired nonces."""
    storage = InMemoryNonceStorage()
    
    # Create multiple nonces with different expiration times
    expired_nonce = Nonce(expires_in=1)
    valid_nonce = Nonce(expires_in=3600)
    
    import time
    time.sleep(1.1)  # Wait for first nonce to expire
    
    storage.store_nonce(expired_nonce)
    storage.store_nonce(valid_nonce)
    
    removed_count = storage.cleanup_expired_nonces()
    
    assert removed_count == 1
    assert storage.get_nonce(valid_nonce.value) is not None
    assert storage.get_nonce(expired_nonce.value) is None