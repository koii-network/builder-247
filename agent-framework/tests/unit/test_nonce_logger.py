import pytest
import uuid
import logging
from datetime import datetime, timezone

from prometheus_swarm.utils.nonce_logger import NonceEventLogger, nonce_logger

class TestNonceEventLogger:
    def test_log_event_returns_valid_nonce(self):
        """Test that log_event returns a valid UUID"""
        nonce = nonce_logger.log_event(
            event_type='test_event', 
            description='A test event'
        )
        
        # Verify it's a valid UUID
        assert uuid.UUID(nonce)
    
    def test_log_event_with_metadata(self):
        """Test logging an event with metadata"""
        metadata = {'user_id': 123, 'action': 'login'}
        nonce = nonce_logger.log_event(
            event_type='user_action', 
            description='User logged in',
            metadata=metadata
        )
        
        assert uuid.UUID(nonce)
    
    def test_log_error_returns_valid_nonce(self):
        """Test that log_error returns a valid UUID"""
        nonce = nonce_logger.log_error(
            error_type='validation_error', 
            error_message='Invalid input'
        )
        
        # Verify it's a valid UUID
        assert uuid.UUID(nonce)
    
    def test_log_error_with_metadata(self):
        """Test logging an error with metadata"""
        metadata = {'input': '123abc', 'validation_rule': 'must be numeric'}
        nonce = nonce_logger.log_error(
            error_type='validation_error', 
            error_message='Invalid input',
            metadata=metadata
        )
        
        assert uuid.UUID(nonce)
    
    def test_nonce_is_unique(self):
        """Ensure each log generates a unique nonce"""
        event_nonces = set()
        error_nonces = set()
        
        # Log multiple events and errors
        for _ in range(100):
            event_nonces.add(nonce_logger.log_event(
                event_type='test', 
                description='Uniqueness test'
            ))
            error_nonces.add(nonce_logger.log_error(
                error_type='test', 
                error_message='Uniqueness test'
            ))
        
        # All nonces should be unique
        assert len(event_nonces) == 100
        assert len(error_nonces) == 100
        assert len(event_nonces.intersection(error_nonces)) == 0
    
    def test_timestamp_is_utc(self):
        """Verify timestamps are in UTC"""
        # Capture logging output
        test_logger = logging.getLogger('test_logger')
        test_logger.setLevel(logging.INFO)
        
        event_logger = NonceEventLogger(logger_name='test_logger')
        
        # Temporarily capture log
        with self._capture_logs(test_logger) as captured_logs:
            event_logger.log_event(
                event_type='timestamp_test', 
                description='UTC timestamp verification'
            )
        
        # Check the logged message
        assert len(captured_logs) == 1
        log_record = captured_logs[0]
        
        # Check that timestamp is parseable and in UTC
        timestamp_str = eval(log_record)['timestamp']
        timestamp = datetime.fromisoformat(timestamp_str)
        assert timestamp.tzinfo == timezone.utc
    
    @staticmethod
    def _capture_logs(logger):
        """Context manager to capture log records"""
        class LogCapture:
            def __init__(self, logger):
                self.logger = logger
                self.captured = []
                self.handler = None
            
            def __enter__(self):
                self.handler = logging.StreamHandler()
                self.handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(message)s')
                self.handler.setFormatter(formatter)
                
                def custom_emit(record):
                    self.captured.append(record.getMessage())
                
                self.handler.emit = custom_emit
                self.logger.addHandler(self.handler)
                return self.captured
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.logger.removeHandler(self.handler)
        
        return LogCapture(logger)