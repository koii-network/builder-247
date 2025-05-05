import pytest
import logging
from io import StringIO
import sys

from prometheus_swarm.utils.joke_filter_logger import JokeFilterLogger

class TestJokeFilterLogger:
    def test_logger_creation(self):
        """Test basic logger creation"""
        logger = JokeFilterLogger()
        assert logger.logger is not None
        assert logger.blocked_words == []
        assert logger.blocked_categories == []
    
    def test_add_blocked_word(self):
        """Test adding blocked words"""
        logger = JokeFilterLogger()
        logger.add_blocked_word('bad')
        assert 'bad' in logger.blocked_words
        
        # Adding same word twice should not create duplicates
        logger.add_blocked_word('bad')
        assert logger.blocked_words.count('bad') == 1
    
    def test_add_blocked_category(self):
        """Test adding blocked categories"""
        logger = JokeFilterLogger()
        logger.add_blocked_category('racist')
        assert 'racist' in logger.blocked_categories
        
        # Adding same category twice should not create duplicates
        logger.add_blocked_category('racist')
        assert logger.blocked_categories.count('racist') == 1
    
    def test_is_joke_acceptable(self):
        """Test joke acceptability checks"""
        logger = JokeFilterLogger(
            blocked_words=['bad', 'offensive'],
            blocked_categories=['racist', 'sexist']
        )
        
        # Acceptable joke
        assert logger.is_joke_acceptable('Why did the chicken cross the road?') is True
        
        # Joke with blocked word
        assert logger.is_joke_acceptable('This is a bad joke') is False
        
        # Joke with blocked category
        assert logger.is_joke_acceptable('A racist joke', categories=['racist']) is False
    
    def test_log_joke_with_logging(self, caplog):
        """Test logging jokes and capturing log output"""
        caplog.set_level(logging.INFO)
        
        logger = JokeFilterLogger()
        
        # Log an acceptable joke
        joke = 'Why did the programmer quit his job? Because he didn\'t get arrays!'
        result = logger.log_joke(joke)
        
        assert result == joke
        assert joke in caplog.text
    
    def test_log_joke_filtered(self, caplog):
        """Test filtering out jokes"""
        caplog.set_level(logging.INFO)
        
        logger = JokeFilterLogger(blocked_words=['bad'])
        
        # Log a filtered joke
        joke = 'This is a bad joke'
        result = logger.log_joke(joke)
        
        assert result is None
        assert joke not in caplog.text
    
    def test_custom_log_level(self, caplog):
        """Test logging with a custom log level"""
        caplog.set_level(logging.ERROR)
        
        logger = JokeFilterLogger()
        joke = 'A very serious joke'
        
        # Log with ERROR level
        result = logger.log_joke(joke, log_level=logging.ERROR)
        
        assert result == joke
        assert joke in caplog.text