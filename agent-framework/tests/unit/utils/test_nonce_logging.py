import pytest
import uuid
import logging
from datetime import datetime, timezone
from prometheus_swarm.utils.nonce_logging import NonceEventLogger

class TestNonceEventLogger:
    def setup_method(self):
        """Setup method to create a fresh NonceEventLogger for each test."""
        self.logger = NonceEventLogger()

    def test_log_event_generates_valid_nonce(self):
        """Test that log_event generates a valid UUID nonce when not provided."""
        event_type = 'test_event'
        nonce = self.logger.log_event(event_type)
        
        assert self.logger.validate_nonce(nonce)
        assert isinstance(nonce, str)

    def test_log_event_with_existing_nonce(self):
        """Test logging an event with an existing nonce."""
        event_type = 'existing_nonce_event'
        custom_nonce = str(uuid.uuid4())
        nonce = self.logger.log_event(event_type, nonce=custom_nonce)
        
        assert nonce == custom_nonce

    def test_log_event_with_context(self):
        """Test logging an event with additional context."""
        event_type = 'context_event'
        context = {
            'user_id': 'test_user',
            'operation': 'create'
        }
        nonce = self.logger.log_event(event_type, context=context)
        
        assert self.logger.validate_nonce(nonce)

    def test_validate_nonce(self):
        """Test nonce validation."""
        # Valid UUIDs
        valid_nonces = [
            str(uuid.uuid4()),
            str(uuid.uuid1()),
            str(uuid.uuid3(uuid.NAMESPACE_DNS, 'test.com')),
            str(uuid.uuid5(uuid.NAMESPACE_DNS, 'test.com'))
        ]

        # Invalid nonces
        invalid_nonces = [
            'not-a-uuid',
            '123456',
            '',
            None
        ]

        for nonce in valid_nonces:
            assert self.logger.validate_nonce(nonce), f"Failed to validate {nonce}"

        for nonce in invalid_nonces:
            assert not self.logger.validate_nonce(nonce), f"Incorrectly validated {nonce}"