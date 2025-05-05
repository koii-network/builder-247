import logging
import pytest
from prometheus_swarm.utils.dad_joke_logging import DadJokeLogger

class TestDadJokeLogger:
    @pytest.fixture
    def dad_joke_logger(self):
        """Create a DadJokeLogger instance for testing."""
        return DadJokeLogger()
    
    def test_logger_initialization(self, dad_joke_logger):
        """Test that the logger is correctly initialized."""
        assert dad_joke_logger.logger is not None
        assert dad_joke_logger.logger.name == 'dad_joke_logger'
        assert dad_joke_logger.logger.level == logging.INFO
    
    def test_log_joke_retrieval(self, dad_joke_logger, caplog):
        """Test logging joke retrieval."""
        caplog.set_level(logging.INFO)
        
        dad_joke_logger.log_joke_retrieval('api', 'joke123')
        
        assert 'Dad Joke Retrieved' in caplog.text
        assert 'source: api' in caplog.text
        assert 'joke_id: joke123' in caplog.text
    
    def test_log_joke_generation(self, dad_joke_logger, caplog):
        """Test logging joke generation."""
        caplog.set_level(logging.INFO)
        
        dad_joke_logger.log_joke_generation('gpt', 0.5)
        
        assert 'Dad Joke Generated' in caplog.text
        assert 'method: gpt' in caplog.text
        assert 'generation_time_seconds: 0.5' in caplog.text
    
    def test_log_joke_usage(self, dad_joke_logger, caplog):
        """Test logging joke usage."""
        caplog.set_level(logging.INFO)
        
        dad_joke_logger.log_joke_usage('conversation', {'mood': 'happy'})
        
        assert 'Dad Joke Used' in caplog.text
        assert 'context: conversation' in caplog.text
        assert 'mood: happy' in caplog.text
    
    def test_log_joke_error(self, dad_joke_logger, caplog):
        """Test logging joke errors."""
        caplog.set_level(logging.ERROR)
        
        dad_joke_logger.log_joke_error('network', 'Failed to fetch joke')
        
        assert 'Dad Joke Error' in caplog.text
        assert 'error_type: network' in caplog.text
        assert 'error_message: Failed to fetch joke' in caplog.text
    
    def test_multiple_logger_instances(self):
        """Ensure multiple logger instances work correctly."""
        logger1 = DadJokeLogger()
        logger2 = DadJokeLogger('custom_dad_joke_logger')
        
        assert logger1.logger.name == 'dad_joke_logger'
        assert logger2.logger.name == 'custom_dad_joke_logger'