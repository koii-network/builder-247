import pytest
import time
from prometheus_swarm.utils.nonce_cache import NonceCache

@pytest.fixture
def nonce_cache():
    """Fixture to create a NonceCache instance with short expiry for testing."""
    return NonceCache(nonce_expiry=1)  # Short expiry for testing

def test_store_nonce(nonce_cache):
    """Test storing a nonce."""
    nonce = "test_nonce_1"
    assert nonce_cache.store_nonce(nonce) == True
    assert nonce_cache.is_nonce_used(nonce) == True

def test_duplicate_nonce(nonce_cache):
    """Test that a duplicate nonce cannot be stored."""
    nonce = "test_nonce_2"
    assert nonce_cache.store_nonce(nonce) == True
    assert nonce_cache.store_nonce(nonce) == False

def test_nonce_expiry(nonce_cache):
    """Test that nonces expire."""
    nonce = "test_nonce_3"
    assert nonce_cache.store_nonce(nonce) == True
    time.sleep(2)  # Wait for nonce to expire
    assert nonce_cache.is_nonce_used(nonce) == False

def test_invalidate_nonce(nonce_cache):
    """Test manual nonce invalidation."""
    nonce = "test_nonce_4"
    assert nonce_cache.store_nonce(nonce) == True
    assert nonce_cache.invalidate_nonce(nonce) == True
    assert nonce_cache.is_nonce_used(nonce) == False

def test_clear_all_nonces(nonce_cache):
    """Test clearing all nonces."""
    nonces = ["nonce_1", "nonce_2", "nonce_3"]
    for nonce in nonces:
        nonce_cache.store_nonce(nonce)
    
    deleted_count = nonce_cache.clear_all_nonces()
    assert deleted_count == len(nonces)

def test_empty_nonce_raises_error(nonce_cache):
    """Test that empty nonce raises a ValueError."""
    with pytest.raises(ValueError):
        nonce_cache.store_nonce("")
    
    with pytest.raises(ValueError):
        nonce_cache.is_nonce_used("")
    
    with pytest.raises(ValueError):
        nonce_cache.invalidate_nonce("")