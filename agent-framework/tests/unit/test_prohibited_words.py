"""
Unit tests for the ProhibitedWordsConfig class.

These tests verify the functionality of the prohibited words configuration
and checking mechanism.
"""

import pytest
from prometheus_swarm.config.prohibited_words import ProhibitedWordsConfig


def test_empty_prohibited_words_config():
    """Test creating a ProhibitedWordsConfig with no initial words."""
    config = ProhibitedWordsConfig()
    assert config.prohibited_words == []
    assert config.check_text("Hello world") is True


def test_init_with_prohibited_words():
    """Test initializing ProhibitedWordsConfig with initial words."""
    config = ProhibitedWordsConfig(["bad", "inappropriate"])
    assert set(config.prohibited_words) == {"bad", "inappropriate"}


def test_add_prohibited_word():
    """Test adding a single prohibited word."""
    config = ProhibitedWordsConfig()
    config.add_prohibited_word("secret")
    assert "secret" in config.prohibited_words


def test_add_prohibited_words():
    """Test adding multiple prohibited words."""
    config = ProhibitedWordsConfig()
    config.add_prohibited_words(["confidential", "private"])
    assert set(config.prohibited_words) == {"confidential", "private"}


def test_check_text_no_prohibited_words():
    """Test that text passes when no prohibited words are present."""
    config = ProhibitedWordsConfig(["bad", "wrong"])
    assert config.check_text("This is a good text") is True


def test_check_text_with_prohibited_words():
    """Test that text fails when prohibited words are present."""
    config = ProhibitedWordsConfig(["bad", "wrong"])
    assert config.check_text("This is a bad text") is False
    assert config.check_text("Wrong example here") is False


def test_check_text_case_insensitive():
    """Test that prohibited words check is case-insensitive."""
    config = ProhibitedWordsConfig(["secret"])
    assert config.check_text("This contains a SECRET word") is False
    assert config.check_text("This contains a Secret word") is False


def test_add_word_with_whitespace():
    """Test that words are stripped of whitespace."""
    config = ProhibitedWordsConfig()
    config.add_prohibited_word("  private  ")
    assert "private" in config.prohibited_words
    assert config.check_text("This contains a private text") is False


def test_multiple_check_scenarios():
    """Test various scenarios of text checking."""
    config = ProhibitedWordsConfig(["bad", "wrong", "secret"])
    
    test_cases = [
        ("This is a good text", True),
        ("This contains a bad word", False),
        ("Another WRONG example", False),
        ("Hidden SECRET message", False),
        ("Mix of good and bad words", False)
    ]
    
    for text, expected in test_cases:
        assert config.check_text(text) is expected