import pytest
import logging
import json
from datetime import datetime, timezone
from prometheus_swarm.utils.nonce_logging import NonceEventLogger

def test_nonce_event_logger_initialization():
    """Test initialization of NonceEventLogger"""
    logger = NonceEventLogger()
    assert isinstance(logger, NonceEventLogger)
    assert logger.logger.name == 'nonce_event_logger'

def test_log_event_generates_unique_nonce():
    """Test that log_event generates unique nonces"""
    logger = NonceEventLogger()
    
    # Log multiple events
    nonce1 = logger.log_event('test_event1')
    nonce2 = logger.log_event('test_event2')
    
    assert nonce1 != nonce2
    assert len(nonce1) > 0
    assert len(nonce2) > 0

def test_log_event_with_context():
    """Test logging an event with additional context"""
    logger = NonceEventLogger()
    
    context = {
        'user_id': 'test_user',
        'action': 'login'
    }
    
    nonce = logger.log_event('login', context, severity='INFO')
    
    # Verify nonce is valid
    assert logger.verify_nonce(nonce)

def test_verify_nonce():
    """Test nonce verification"""
    logger = NonceEventLogger()
    
    # Valid nonce
    valid_nonce = logger.log_event('test_event')
    assert logger.verify_nonce(valid_nonce) is True
    
    # Invalid nonces
    invalid_nonces = [
        '',
        'not-a-uuid',
        '12345',
        None
    ]
    
    for invalid_nonce in invalid_nonces:
        assert logger.verify_nonce(invalid_nonce) is False

def test_log_event_severity_levels():
    """Test logging with different severity levels"""
    logger = NonceEventLogger()
    
    severity_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    for severity in severity_levels:
        nonce = logger.log_event('test_event', severity=severity)
        assert logger.verify_nonce(nonce)

def test_log_event_context_serialization():
    """Test that context can be serialized and contains correct information"""
    logger = NonceEventLogger()
    
    complex_context = {
        'nested': {
            'key1': 'value1',
            'key2': 42
        },
        'list': [1, 2, 3],
        'string': 'test'
    }
    
    nonce = logger.log_event('complex_event', complex_context)
    
    # Verify nonce is valid
    assert logger.verify_nonce(nonce)