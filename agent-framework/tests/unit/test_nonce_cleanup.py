import pytest
from datetime import datetime, timedelta
from prometheus_swarm.jobs.nonce_cleanup import NonceCleanupJob

def test_nonce_cleanup_job_initialization():
    """Test initialization of NonceCleanupJob."""
    nonce_store = {}
    job = NonceCleanupJob(nonce_store)
    assert job.nonce_store == nonce_store
    assert job.expiration_hours == 24

def test_find_expired_nonces():
    """Test finding expired nonces."""
    current_time = datetime.now()
    nonce_store = {
        'nonce1': {'timestamp': current_time - timedelta(hours=25)},
        'nonce2': {'timestamp': current_time - timedelta(hours=23)},
        'nonce3': {'timestamp': current_time - timedelta(hours=26)}
    }
    
    job = NonceCleanupJob(nonce_store, expiration_hours=24)
    expired_nonces = job.find_expired_nonces()
    
    assert set(expired_nonces) == {'nonce1', 'nonce3'}

def test_cleanup_removes_expired_nonces():
    """Test cleanup method removes expired nonces."""
    current_time = datetime.now()
    nonce_store = {
        'nonce1': {'timestamp': current_time - timedelta(hours=25)},
        'nonce2': {'timestamp': current_time - timedelta(hours=23)},
        'nonce3': {'value': 'something_else'}  # No timestamp
    }
    
    job = NonceCleanupJob(nonce_store, expiration_hours=24)
    removed_count = job.cleanup()
    
    assert removed_count == 1
    assert list(nonce_store.keys()) == ['nonce2', 'nonce3']

def test_cleanup_with_no_expired_nonces():
    """Test cleanup when no nonces are expired."""
    current_time = datetime.now()
    nonce_store = {
        'nonce1': {'timestamp': current_time - timedelta(hours=23)},
        'nonce2': {'timestamp': current_time - timedelta(hours=22)}
    }
    
    job = NonceCleanupJob(nonce_store, expiration_hours=24)
    removed_count = job.cleanup()
    
    assert removed_count == 0
    assert len(nonce_store) == 2

def test_custom_expiration_time():
    """Test cleanup with custom expiration time."""
    current_time = datetime.now()
    nonce_store = {
        'nonce1': {'timestamp': current_time - timedelta(hours=2)},
        'nonce2': {'timestamp': current_time - timedelta(hours=1)}
    }
    
    job = NonceCleanupJob(nonce_store, expiration_hours=1.5)
    removed_count = job.cleanup()
    
    assert removed_count == 1
    assert list(nonce_store.keys()) == ['nonce2']