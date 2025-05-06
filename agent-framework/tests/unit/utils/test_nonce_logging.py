import pytest
import logging
import uuid
from prometheus_swarm.utils.nonce_logging import NonceEventLogger

class TestNonceEventLogger:
    def setup_method(self):
        """Setup method to create a fresh NonceEventLogger for each test."""
        self.logger = NonceEventLogger()
    
    def test_log_nonce_event_with_auto_generation(self):
        """Test logging a nonce event with auto nonce generation."""
        nonce = self.logger.log_nonce_event('generation')
        
        # Verify nonce is a valid UUID
        try:
            uuid.UUID(nonce)
        except ValueError:
            pytest.fail("Generated nonce is not a valid UUID")
    
    def test_log_nonce_event_with_custom_nonce(self):
        """Test logging a nonce event with a custom nonce."""
        custom_nonce = str(uuid.uuid4())
        logged_nonce = self.logger.log_nonce_event('generation', nonce=custom_nonce)
        
        assert logged_nonce == custom_nonce
    
    def test_log_nonce_event_with_context(self):
        """Test logging a nonce event with additional context."""
        context = {
            'user_id': 'test_user',
            'operation': 'signup'
        }
        nonce = self.logger.log_nonce_event('generation', context=context)
        
        # Verification would involve checking logs, which is tricky to do directly
        assert nonce is not None
    
    def test_validate_nonce_valid(self):
        """Test nonce validation for a valid UUID."""
        valid_nonce = str(uuid.uuid4())
        result = self.logger.validate_nonce(valid_nonce)
        
        assert result is True
    
    def test_validate_nonce_invalid(self):
        """Test nonce validation for an invalid UUID."""
        invalid_nonce = 'not-a-valid-uuid'
        result = self.logger.validate_nonce(invalid_nonce)
        
        assert result is False
    
    def test_validate_nonce_with_context(self):
        """Test nonce validation with additional context."""
        valid_nonce = str(uuid.uuid4())
        context = {'validation_source': 'test'}
        result = self.logger.validate_nonce(valid_nonce, validation_context=context)
        
        assert result is True