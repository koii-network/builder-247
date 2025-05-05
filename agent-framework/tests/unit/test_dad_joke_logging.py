import time
import logging
from unittest.mock import patch
import pytest

from prometheus_swarm.utils.dad_joke_logging import DadJokeLogger, dad_joke_logger

def test_dad_joke_logger_initialization():
    """Test that the DadJokeLogger is initialized correctly."""
    logger = DadJokeLogger()
    assert logger.logger.name == 'dad_joke_logger'
    assert logger.logger.level == logging.INFO
    assert len(logger.logger.handlers) > 0

@patch('logging.Logger.info')
def test_log_joke_retrieval(mock_info):
    """Test logging of joke retrieval."""
    logger = DadJokeLogger()
    logger.reset_metrics()
    
    joke = "Why don't scientists trust atoms? Because they make up everything!"
    logger.log_joke_retrieval(joke, source='test')
    
    # Check metrics
    metrics = logger.get_metrics()
    assert metrics['total_jokes_retrieved'] == 1
    assert metrics['last_joke_retrieval_time'] is not None
    
    # Verify log was called
    mock_info.assert_called_once_with(f"Dad Joke retrieved from test: {joke}")

@patch('logging.Logger.info')
def test_log_joke_generation(mock_info):
    """Test logging of joke generation."""
    logger = DadJokeLogger()
    logger.reset_metrics()
    
    joke = "I told my wife she was drawing her eyebrows too high. She looked surprised."
    model = 'test_model'
    logger.log_joke_generation(joke, model)
    
    # Check metrics
    metrics = logger.get_metrics()
    assert metrics['total_jokes_generated'] == 1
    
    # Verify log was called
    mock_info.assert_called_once_with(f"Dad Joke generated using {model}: {joke}")

@patch('logging.Logger.error')
def test_log_retrieval_error(mock_error):
    """Test logging of retrieval errors."""
    logger = DadJokeLogger()
    logger.reset_metrics()
    
    error_msg = "Failed to retrieve joke"
    logger.log_retrieval_error(error_msg)
    
    # Check metrics
    metrics = logger.get_metrics()
    assert metrics['total_retrieval_errors'] == 1
    
    # Verify log was called
    mock_error.assert_called_once_with(f"Dad Joke Retrieval Error: {error_msg}")

def test_metrics_reset():
    """Test resetting of metrics."""
    logger = DadJokeLogger()
    
    # Perform some logging operations
    logger.log_joke_retrieval("Test joke")
    logger.log_joke_generation("Generated joke", "test_model")
    logger.log_retrieval_error("Test error")
    
    # Reset metrics
    logger.reset_metrics()
    
    # Check that metrics are back to initial state
    metrics = logger.get_metrics()
    assert metrics['total_jokes_retrieved'] == 0
    assert metrics['total_jokes_generated'] == 0
    assert metrics['last_joke_retrieval_time'] is None
    assert metrics['total_retrieval_errors'] == 0

def test_global_logger_exists():
    """Test that the global dad_joke_logger is available."""
    assert isinstance(dad_joke_logger, DadJokeLogger)
    assert dad_joke_logger.logger.name == 'dad_joke_logger'