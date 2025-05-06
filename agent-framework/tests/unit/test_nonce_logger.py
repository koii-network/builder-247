import os
import json
import logging
import tempfile
import uuid
from datetime import datetime, timezone

import pytest

from prometheus_swarm.utils.nonce_logger import NonceEventLogger

def test_nonce_event_logger_initialization():
    """Test initialization of NonceEventLogger with default parameters."""
    logger = NonceEventLogger()
    assert logger.enable_json_logs is True
    assert logger.logger.level == logging.INFO
    assert os.path.exists(os.path.join('logs', 'nonce_events'))

def test_nonce_event_logging():
    """Test logging a nonce event with default parameters."""
    logger = NonceEventLogger()
    
    details = {
        'nonce': str(uuid.uuid4()),
        'client_id': 'test_client'
    }
    
    event_id = logger.log_nonce_event('generation', details)
    
    # Verify event ID is valid UUID
    assert uuid.UUID(event_id)

def test_nonce_event_logging_with_custom_log_dir():
    """Test logging with a custom log directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = NonceEventLogger(log_dir=tmpdir, enable_json_logs=True)
        
        details = {
            'nonce': str(uuid.uuid4()),
            'client_id': 'test_client'
        }
        
        logger.log_nonce_event('generation', details)
        
        # Check JSON log file was created
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        log_file_path = os.path.join(tmpdir, f'nonce_events_{timestamp}.json')
        
        assert os.path.exists(log_file_path)
        
        # Verify log entry
        with open(log_file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            log_entry = json.loads(lines[-1])
            
            assert 'event_id' in log_entry
            assert log_entry['event_type'] == 'generation'
            assert log_entry['details']['client_id'] == 'test_client'

def test_nonce_event_logging_different_severities():
    """Test logging events with different severity levels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = NonceEventLogger(log_dir=tmpdir, log_level=logging.DEBUG)
        
        info_details = {'message': 'Info level event'}
        warn_details = {'message': 'Warning level event'}
        error_details = {'message': 'Error level event'}
        
        # Should not raise any exceptions
        logger.log_nonce_event('info_event', info_details, severity='INFO')
        logger.log_nonce_event('warn_event', warn_details, severity='WARNING')
        logger.log_nonce_event('error_event', error_details, severity='ERROR')

def test_nonce_event_logging_disabled_json():
    """Test logging with JSON logs disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = NonceEventLogger(log_dir=tmpdir, enable_json_logs=False)
        
        details = {
            'nonce': str(uuid.uuid4()),
            'client_id': 'test_client'
        }
        
        logger.log_nonce_event('generation', details)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        log_file_path = os.path.join(tmpdir, f'nonce_events_{timestamp}.json')
        
        # Verify no log file was created
        assert not os.path.exists(log_file_path)

def test_nonce_event_logging_error_handling():
    """Test error handling during JSON logging."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a read-only directory to simulate write failure
        os.chmod(tmpdir, 0o444)
        
        logger = NonceEventLogger(log_dir=tmpdir, enable_json_logs=True)
        
        details = {
            'nonce': str(uuid.uuid4()),
            'client_id': 'test_client'
        }
        
        # Should not raise an exception, just log the error
        logger.log_nonce_event('generation', details)