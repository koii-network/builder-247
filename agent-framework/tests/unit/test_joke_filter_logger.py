import logging
import pytest
import io
from unittest.mock import patch
from prometheus_swarm.utils.joke_filter_logger import JokeFilterLogger

class TestJokeFilterLogger:
    @pytest.fixture
    def log_capture(self):
        """Create a log capture stream for testing."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('test_logger')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return log_stream, logger
    
    def test_log_serious_message(self, log_capture):
        """Test that serious messages are logged."""
        log_stream, base_logger = log_capture
        joke_logger = JokeFilterLogger('test_logger')
        joke_logger.logger = base_logger
        
        joke_logger.info("System performance is improving")
        log_stream.seek(0)
        logged_message = log_stream.read().strip()
        
        assert "System performance is improving" in logged_message
    
    def test_filter_joke_messages(self, log_capture):
        """Test that joke messages are filtered out."""
        log_stream, base_logger = log_capture
        joke_logger = JokeFilterLogger('test_logger')
        joke_logger.logger = base_logger
        
        joke_logger.info("This is a joke LOL")
        log_stream.seek(0)
        logged_message = log_stream.read().strip()
        
        assert logged_message == ""
    
    def test_custom_joke_patterns(self, log_capture):
        """Test custom joke pattern filtering."""
        log_stream, base_logger = log_capture
        joke_logger = JokeFilterLogger(
            'test_logger', 
            joke_patterns=[r'\bwacky\b']
        )
        joke_logger.logger = base_logger
        
        joke_logger.info("This is a wacky situation")
        log_stream.seek(0)
        logged_message = log_stream.read().strip()
        
        assert logged_message == ""
    
    def test_all_log_levels(self):
        """Test joke filtering for all log levels."""
        with patch.object(logging.Logger, 'log') as mock_log:
            joke_logger = JokeFilterLogger('test_logger')
            
            # Test different log levels
            test_cases = [
                (logging.DEBUG, "Debug joke LOL"),
                (logging.INFO, "Info joke haha"),
                (logging.WARNING, "Warning joke 😂"),
                (logging.ERROR, "Error joke funny"),
                (logging.CRITICAL, "Critical joke funny")
            ]
            
            for level, message in test_cases:
                joke_logger.log(level, message)
                mock_log.assert_not_called, f"Level {level} should filter out jokes"
    
    def test_non_joke_messages_logged(self):
        """Test that non-joke messages are logged at various levels."""
        with patch.object(logging.Logger, 'log') as mock_log:
            joke_logger = JokeFilterLogger('test_logger')
            
            # Test different log levels with serious messages
            test_cases = [
                (logging.DEBUG, "Debug system check"),
                (logging.INFO, "System performance update"),
                (logging.WARNING, "Potential performance bottleneck"),
                (logging.ERROR, "Critical system error"),
                (logging.CRITICAL, "Catastrophic system failure")
            ]
            
            for level, message in test_cases:
                joke_logger.log(level, message)
                mock_log.assert_called, f"Level {level} should log serious messages"
    
    def test_logging_methods(self):
        """Test specific logging method wrappers."""
        with patch.object(JokeFilterLogger, 'log') as mock_log:
            joke_logger = JokeFilterLogger('test_logger')
            
            test_cases = [
                (joke_logger.debug, "Debug message"),
                (joke_logger.info, "Info message"),
                (joke_logger.warning, "Warning message"),
                (joke_logger.error, "Error message"),
                (joke_logger.critical, "Critical message")
            ]
            
            for method, message in test_cases:
                method(message)
                mock_log.assert_called_once