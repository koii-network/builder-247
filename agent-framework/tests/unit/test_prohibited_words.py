"""
Unit tests for ProhibitedWordsConfig.
"""
import pytest
from prometheus_swarm.config.prohibited_words import ProhibitedWordsConfig

def test_init_empty_configuration():
    """Test initializing configuration with no words."""
    config = ProhibitedWordsConfig()
    assert config.get_prohibited_words() == []

def test_init_with_words():
    """Test initializing configuration with words."""
    words = ['bad', 'inappropriate']
    config = ProhibitedWordsConfig(words)
    assert set(config.get_prohibited_words()) == {'bad', 'inappropriate'}

def test_case_insensitive_matching():
    """Test case-insensitive prohibited word matching."""
    config = ProhibitedWordsConfig(['Bad', 'Wrong'])
    
    assert config.is_text_prohibited('This is a bad example') is True
    assert config.is_text_prohibited('This is a BAD example') is True
    assert config.is_text_prohibited('This is fine') is False

def test_add_prohibited_word():
    """Test adding a new prohibited word."""
    config = ProhibitedWordsConfig()
    config.add_prohibited_word('Offensive')
    
    assert 'offensive' in config.get_prohibited_words()

def test_add_duplicate_word():
    """Test adding a duplicate prohibited word."""
    config = ProhibitedWordsConfig(['bad'])
    config.add_prohibited_word('Bad')
    
    assert config.get_prohibited_words().count('bad') == 1

def test_remove_prohibited_word():
    """Test removing a prohibited word."""
    config = ProhibitedWordsConfig(['bad', 'wrong'])
    config.remove_prohibited_word('bad')
    
    assert 'bad' not in config.get_prohibited_words()
    assert 'wrong' in config.get_prohibited_words()

def test_is_text_prohibited():
    """Test text prohibition checking."""
    config = ProhibitedWordsConfig(['bad', 'wrong'])
    
    assert config.is_text_prohibited('This is a bad example') is True
    assert config.is_text_prohibited('Everything is wrong here') is True
    assert config.is_text_prohibited('This is fine') is False

def test_empty_text_handling():
    """Test handling of empty text."""
    config = ProhibitedWordsConfig(['bad'])
    
    assert config.is_text_prohibited('') is False
    assert config.is_text_prohibited(None) is False