"""
Unit tests for JokeFilterLogger.
"""

import logging
import pytest
from prometheus_swarm.utils.joke_filter_logger import JokeFilterLogger


def test_joke_filter_logger_init():
    """Test initialization of JokeFilterLogger."""
    logger = JokeFilterLogger()
    assert logger.filters == []
    assert isinstance(logger.logger, logging.Logger)


def test_is_joke_safe():
    """Test joke safety filtering."""
    logger = JokeFilterLogger(filters=["inappropriate", "offensive"])
    
    # Safe jokes
    assert logger.is_joke_safe("Why did the chicken cross the road?")
    assert logger.is_joke_safe("A funny clean joke")
    
    # Unsafe jokes
    assert not logger.is_joke_safe("An inappropriate joke")
    assert not logger.is_joke_safe("Offensive content here")


def test_log_joke_safe_logging(caplog):
    """Test safe logging functionality."""
    caplog.set_level(logging.INFO)
    
    joke_logger = JokeFilterLogger()
    safe_joke = "Why did the programmer quit his job? Because he didn't get arrays!"
    
    joke_logger.log_joke(safe_joke)
    
    assert len(caplog.records) == 1
    assert safe_joke in caplog.text


def test_log_joke_filter_raises_error():
    """Test that logging filtered jokes raises an error."""
    joke_logger = JokeFilterLogger(filters=["bad"])
    bad_joke = "This is a bad joke"
    
    with pytest.raises(ValueError, match="Joke contains filtered content."):
        joke_logger.log_joke(bad_joke)


def test_add_filter():
    """Test adding a new filter keyword."""
    joke_logger = JokeFilterLogger()
    assert len(joke_logger.filters) == 0
    
    joke_logger.add_filter("naughty")
    assert len(joke_logger.filters) == 1
    assert "naughty" in joke_logger.filters


def test_log_joke_custom_logger(mocker):
    """Test logging with a custom logger."""
    mock_logger = mocker.Mock()
    joke_logger = JokeFilterLogger(logger=mock_logger)
    
    safe_joke = "A clean joke about programming"
    joke_logger.log_joke(safe_joke)
    
    mock_logger.log.assert_called_once_with(
        logging.INFO, safe_joke
    )