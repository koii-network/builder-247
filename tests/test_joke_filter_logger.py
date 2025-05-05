import pytest
import logging
from src.joke_filter_logger import JokeFilterLogger

def test_joke_filter_logger_initialization():
    """Test JokeFilterLogger basic initialization"""
    logger = JokeFilterLogger()
    assert isinstance(logger, JokeFilterLogger)
    assert logger.bad_words == ['racist', 'sexist', 'offensive']

def test_joke_filter_custom_bad_words():
    """Test custom bad words initialization"""
    custom_bad_words = ['inappropriate', 'mean']
    logger = JokeFilterLogger(bad_words=custom_bad_words)
    assert logger.bad_words == custom_bad_words

def test_filter_joke_passes_clean_joke():
    """Test that a clean joke passes filtering"""
    logger = JokeFilterLogger()
    clean_joke = "Why did the chicken cross the road?"
    assert logger.filter_joke(clean_joke) == clean_joke

def test_filter_joke_filters_bad_words():
    """Test that jokes with bad words are filtered out"""
    logger = JokeFilterLogger()
    offensive_joke = "This is a racist joke about minorities"
    assert logger.filter_joke(offensive_joke) is None

def test_filter_joke_case_insensitive():
    """Test that bad word filtering is case-insensitive"""
    logger = JokeFilterLogger()
    offensive_joke = "This is a RACIST joke"
    assert logger.filter_joke(offensive_joke) is None

def test_batch_filter_jokes():
    """Test batch joke filtering"""
    logger = JokeFilterLogger()
    jokes = [
        "A funny clean joke",
        "An offensive racist joke",
        "Another clean joke"
    ]
    filtered_jokes = logger.batch_filter_jokes(jokes)
    assert len(filtered_jokes) == 2
    assert "offensive racist joke" not in filtered_jokes

def test_filter_joke_handles_invalid_input():
    """Test handling of invalid joke inputs"""
    logger = JokeFilterLogger()
    assert logger.filter_joke(None) is None
    assert logger.filter_joke("") is None
    assert logger.filter_joke(123) is None

def test_batch_filter_empty_list():
    """Test batch filtering with an empty list"""
    logger = JokeFilterLogger()
    assert logger.batch_filter_jokes([]) == []
    assert logger.batch_filter_jokes(None) == []