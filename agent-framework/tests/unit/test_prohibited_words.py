"""
Unit tests for the ProhibitedWordsConfig utility.
"""

import pytest
from prometheus_swarm.utils.prohibited_words import ProhibitedWordsConfig


def test_initialization():
    """Test initialization of ProhibitedWordsConfig."""
    config = ProhibitedWordsConfig()
    assert config.get_prohibited_words() == []

    words = ['bad', 'offensive']
    config = ProhibitedWordsConfig(words)
    assert set(config.get_prohibited_words()) == {'bad', 'offensive'}


def test_add_prohibited_word():
    """Test adding a prohibited word."""
    config = ProhibitedWordsConfig()
    config.add_prohibited_word('spam')
    assert 'spam' in config.get_prohibited_words()
    
    # Adding duplicate should not create multiple entries
    config.add_prohibited_word('spam')
    assert config.get_prohibited_words().count('spam') == 1


def test_remove_prohibited_word():
    """Test removing a prohibited word."""
    config = ProhibitedWordsConfig(['bad', 'word'])
    config.remove_prohibited_word('bad')
    assert 'bad' not in config.get_prohibited_words()
    assert 'word' in config.get_prohibited_words()


def test_contains_prohibited_words():
    """Test checking for prohibited words."""
    config = ProhibitedWordsConfig(['bad', 'word'])

    assert config.contains_prohibited_words('this is a bad word')
    assert config.contains_prohibited_words('BAD word here')
    assert not config.contains_prohibited_words('this is good')
    assert not config.contains_prohibited_words('')


def test_replace_prohibited_words():
    """Test replacing prohibited words."""
    config = ProhibitedWordsConfig(['bad', 'word'])

    result = config.replace_prohibited_words('this is a bad word')
    assert result == 'this is a [REDACTED] [REDACTED]'

    result = config.replace_prohibited_words('this is a good sentence', replacement='***')
    assert result == 'this is a good sentence'

    result = config.replace_prohibited_words('BAD WORD', replacement='X')
    assert result == 'X X'


def test_case_insensitivity():
    """Test case-insensitive matching of prohibited words."""
    config = ProhibitedWordsConfig(['spam'])

    assert config.contains_prohibited_words('SPAM alert')
    assert config.contains_prohibited_words('spam ALERT')
    
    result = config.replace_prohibited_words('Spam is not good')
    assert result == '[REDACTED] is not good'