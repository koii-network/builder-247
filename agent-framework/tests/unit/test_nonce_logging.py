import time
import pytest
from prometheus_swarm.utils.nonce_logging import NonceEventLogger

def test_nonce_generation():
    """Test that nonce generation creates unique identifiers."""
    logger = NonceEventLogger()
    nonce1 = logger.generate_nonce()
    nonce2 = logger.generate_nonce()
    
    assert nonce1 != nonce2
    assert len(nonce1) > 0
    assert len(nonce2) > 0

def test_log_and_retrieve_events():
    """Test logging and retrieving nonce events."""
    logger = NonceEventLogger()
    nonce = logger.generate_nonce()
    
    # Log multiple events
    logger.log_event(nonce, 'start', {'info': 'beginning process'})
    logger.log_event(nonce, 'progress', {'step': 1})
    logger.log_event(nonce, 'complete', {'result': 'success'})
    
    # Retrieve events
    events = logger.get_nonce_events(nonce)
    
    assert events is not None
    assert len(events['events']) == 3
    assert events['events'][0]['type'] == 'start'
    assert events['events'][1]['type'] == 'progress'
    assert events['events'][2]['type'] == 'complete'

def test_clear_nonce_events():
    """Test clearing events for a specific nonce."""
    logger = NonceEventLogger()
    nonce = logger.generate_nonce()
    
    logger.log_event(nonce, 'test')
    assert logger.get_nonce_events(nonce) is not None
    
    result = logger.clear_nonce_events(nonce)
    assert result is True
    assert logger.get_nonce_events(nonce) is None

def test_prune_old_events():
    """Test pruning old events based on age."""
    logger = NonceEventLogger()
    
    # Create multiple nonces with different timestamps
    nonce1 = logger.generate_nonce()
    nonce2 = logger.generate_nonce()
    nonce3 = logger.generate_nonce()
    
    # Manipulate internal timestamps for testing
    logger.log_event(nonce1, 'old_event')
    logger._nonce_events[nonce1]['created_at'] = time.time() - 7200  # 2 hours ago
    
    logger.log_event(nonce2, 'recent_event')
    
    logger.log_event(nonce3, 'another_old_event')
    logger._nonce_events[nonce3]['created_at'] = time.time() - 5400  # 1.5 hours ago
    
    # Prune events older than 1 hour
    pruned_count = logger.prune_old_events(max_age_seconds=3600)
    
    assert pruned_count == 2
    assert logger.get_nonce_events(nonce1) is None
    assert logger.get_nonce_events(nonce2) is not None
    assert logger.get_nonce_events(nonce3) is None

def test_thread_safety():
    """Basic thread safety test."""
    from concurrent.futures import ThreadPoolExecutor
    
    logger = NonceEventLogger()
    nonce = logger.generate_nonce()
    
    def log_event(i):
        logger.log_event(nonce, f'thread_{i}')
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(log_event, range(100))
    
    events = logger.get_nonce_events(nonce)
    assert events is not None
    assert len(events['events']) == 100

def test_event_details():
    """Test logging events with various details."""
    logger = NonceEventLogger()
    nonce = logger.generate_nonce()
    
    details = {
        'user_id': 123,
        'operation': 'data_transfer',
        'metadata': {
            'source': 'internal',
            'priority': 'high'
        }
    }
    
    logger.log_event(nonce, 'detailed_event', details)
    
    events = logger.get_nonce_events(nonce)
    assert events is not None
    assert events['events'][0]['details'] == details

def test_nonexistent_nonce_handling():
    """Test handling of nonexistent nonce."""
    logger = NonceEventLogger()
    
    # Attempt to retrieve or clear a nonexistent nonce
    nonexistent_nonce = 'fake-nonce-12345'
    
    assert logger.get_nonce_events(nonexistent_nonce) is None
    assert logger.clear_nonce_events(nonexistent_nonce) is False