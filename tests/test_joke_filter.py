import pytest
import logging
from src.joke_filter import JokeFilter

class TestJokeFilter:
    def test_init_default(self):
        """Test initialization with default parameters."""
        joke_filter = JokeFilter()
        assert joke_filter.offensive_words == []
        assert joke_filter.max_length is None

    def test_init_with_offensive_words(self):
        """Test initialization with offensive words."""
        offensive_words = ["bad", "inappropriate"]
        joke_filter = JokeFilter(offensive_words=offensive_words)
        assert joke_filter.offensive_words == offensive_words

    def test_init_with_max_length(self):
        """Test initialization with max length."""
        max_length = 50
        joke_filter = JokeFilter(max_length=max_length)
        assert joke_filter.max_length == max_length

    def test_joke_appropriate_no_filters(self):
        """Test joke appropriateness with no filtering criteria."""
        joke_filter = JokeFilter()
        joke = "Why did the chicken cross the road?"
        assert joke_filter.is_joke_appropriate(joke) is True

    def test_joke_inappropriate_offensive_word(self):
        """Test joke filtering with offensive words."""
        joke_filter = JokeFilter(offensive_words=["bad"])
        joke = "This is a bad joke"
        assert joke_filter.is_joke_appropriate(joke) is False

    def test_joke_inappropriate_length(self):
        """Test joke filtering with max length."""
        joke_filter = JokeFilter(max_length=10)
        joke = "This is a very long joke that exceeds the max length"
        assert joke_filter.is_joke_appropriate(joke) is False

    def test_filter_jokes(self):
        """Test filtering multiple jokes."""
        jokes = [
            "A clean joke",
            "A bad joke",
            "A very very very long joke that should not pass the length filter"
        ]
        joke_filter = JokeFilter(
            offensive_words=["bad"],
            max_length=20
        )
        filtered_jokes = joke_filter.filter_jokes(jokes)
        assert filtered_jokes == ["A clean joke"]

    def test_case_insensitive_offensive_word(self):
        """Test that offensive word detection is case-insensitive."""
        joke_filter = JokeFilter(offensive_words=["BAD"])
        joke = "this is a bad joke"
        assert joke_filter.is_joke_appropriate(joke) is False

    def test_logger_exists(self):
        """Test that logger is correctly initialized."""
        joke_filter = JokeFilter()
        assert hasattr(joke_filter, 'logger')
        assert isinstance(joke_filter.logger, logging.Logger)