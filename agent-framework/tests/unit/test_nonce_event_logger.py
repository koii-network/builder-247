import logging
import json
import uuid
import pytest
from prometheus_swarm.utils.nonce_event_logger import NonceEventLogger


def test_nonce_event_logger_initialization():
    """Test initialization of NonceEventLogger."""
    logger = NonceEventLogger()
    assert logger.logger is not None
    assert logger.logger.name == 'nonce_event_logger'


def test_log_event_with_minimal_params():
    """Test logging an event with minimal parameters."""
    logger = NonceEventLogger()
    nonce = logger.log_event('generation')
    
    # Validate nonce is a valid UUID
    assert logger.validate_event(nonce)


def test_log_event_with_metadata():
    """Test logging an event with additional metadata."""
    logger = NonceEventLogger()
    metadata = {
        'source': 'authentication',
        'user_id': 'test_user'
    }
    nonce = logger.log_event('validation', metadata)
    
    assert logger.validate_event(nonce)


def test_log_event_invalid_input():
    """Test logging with invalid event types raises ValueError."""
    logger = NonceEventLogger()
    
    with pytest.raises(ValueError, match="Event type must be a non-empty string"):
        logger.log_event('')
    
    with pytest.raises(ValueError, match="Event type must be a non-empty string"):
        logger.log_event(None)


def test_nonce_validation():
    """Test nonce validation method."""
    logger = NonceEventLogger()
    
    # Valid nonce
    valid_nonce = str(uuid.uuid4())
    assert logger.validate_event(valid_nonce) is True
    
    # Invalid nonce formats
    invalid_nonces = [
        'not-a-uuid',
        '12345',
        '',
        None
    ]
    
    for invalid_nonce in invalid_nonces:
        assert logger.validate_event(invalid_nonce) is False


def test_event_structure():
    """Test the structure of logged events."""
    logger = NonceEventLogger()
    metadata = {'test_key': 'test_value'}
    nonce = logger.log_event('rotation', metadata)
    
    # Add a logging handler to capture log messages
    log_capture = logging.getLogger('nonce_event_logger')
    log_capture.propagate = False
    
    # Create a StringIO to capture log messages
    from io import StringIO
    import sys
    log_output = StringIO()
    handler = logging.StreamHandler(log_output)
    log_capture.addHandler(handler)
    
    try:
        logger.log_event('rotation', metadata)
        log_message = log_output.getvalue().strip()
        
        # Parse the log message as JSON
        event_log = json.loads(log_message.split(': ')[-1])
        
        # Validate event log structure
        assert 'nonce' in event_log
        assert 'event_type' in event_log
        assert 'timestamp' in event_log
        assert 'metadata' in event_log
        assert event_log['event_type'] == 'rotation'
        assert event_log['metadata'] == metadata
    finally:
        log_capture.removeHandler(handler)
        handler.close()