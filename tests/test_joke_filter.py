import pytest
import logging
import io
from src.joke_filter import JokeFilter

def test_joke_filter_init():
    """Test initializing JokeFilter with and without a blacklist."""
    # Test default initialization
    joke_filter = JokeFilter()
    assert joke_filter.blacklist == []
    
    # Test initialization with a blacklist
    blacklist = ["bad", "offensive"]
    joke_filter = JokeFilter(blacklist)
    assert joke_filter.blacklist == blacklist

def test_joke_filter_successful():
    """Test filtering a joke that passes the blacklist check."""
    joke_filter = JokeFilter(["bad"])
    joke = "This is a good joke!"
    
    # Capture log messages
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    joke_filter.logger.addHandler(handler)
    joke_filter.logger.setLevel(logging.INFO)
    
    # Test joke filtering
    filtered_joke = joke_filter.filter_joke(joke)
    assert filtered_joke == joke
    
    # Check log message
    log_message = log_capture.getvalue().strip()
    assert f"Joke passed filtering: {joke}" in log_message

def test_joke_filter_blocked():
    """Test filtering a joke that contains a blacklisted word."""
    joke_filter = JokeFilter(["bad"])
    joke = "This is a bad joke!"
    
    # Capture log messages
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    joke_filter.logger.addHandler(handler)
    joke_filter.logger.setLevel(logging.WARNING)
    
    # Test joke filtering
    filtered_joke = joke_filter.filter_joke(joke)
    assert filtered_joke is None
    
    # Check log message
    log_message = log_capture.getvalue().strip()
    assert "Joke filtered due to blacklisted word: bad" in log_message

def test_joke_filter_case_insensitive():
    """Test that filtering is case-insensitive."""
    joke_filter = JokeFilter(["bad"])
    joke = "This is a BAD joke!"
    
    filtered_joke = joke_filter.filter_joke(joke)
    assert filtered_joke is None

def test_add_to_blacklist():
    """Test adding words to the blacklist."""
    joke_filter = JokeFilter()
    
    # Capture log messages
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    joke_filter.logger.addHandler(handler)
    joke_filter.logger.setLevel(logging.INFO)
    
    # Add words to blacklist
    joke_filter.add_to_blacklist(["bad", "offensive"])
    assert "bad" in joke_filter.blacklist
    assert "offensive" in joke_filter.blacklist
    
    # Check log messages
    log_message = log_capture.getvalue().strip()
    assert "Added 'bad' to blacklist" in log_message
    assert "Added 'offensive' to blacklist" in log_message

def test_remove_from_blacklist():
    """Test removing words from the blacklist."""
    joke_filter = JokeFilter(["bad", "offensive"])
    
    # Capture log messages
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    joke_filter.logger.addHandler(handler)
    joke_filter.logger.setLevel(logging.INFO)
    
    # Remove words from blacklist
    joke_filter.remove_from_blacklist(["bad"])
    assert "bad" not in joke_filter.blacklist
    assert "offensive" in joke_filter.blacklist
    
    # Check log messages
    log_message = log_capture.getvalue().strip()
    assert "Removed 'bad' from blacklist" in log_message