"""
Unit tests for ProhibitedWordsConfig.
"""

import pytest
from prometheus_swarm.utils.prohibited_words import ProhibitedWordsConfig

def test_init_empty():
    """Test initializing with no words."""
    config = ProhibitedWordsConfig()
    assert len(config.get_prohibited_words()) == 0

def test_init_with_words():
    """Test initializing with initial words."""
    config = ProhibitedWordsConfig(["bad", "Terrible"])
    prohibited_words = config.get_prohibited_words()
    assert set(prohibited_words) == {"bad", "terrible"}

def test_add_word():
    """Test adding a new prohibited word."""
    config = ProhibitedWordsConfig()
    config.add_word("badword")
    assert "badword" in config.get_prohibited_words()

def test_add_word_case_insensitive():
    """Test that word addition is case-insensitive."""
    config = ProhibitedWordsConfig()
    config.add_word("BadWord")
    config.add_word("badword")
    assert len(config.get_prohibited_words()) == 1

def test_remove_word():
    """Test removing an existing prohibited word."""
    config = ProhibitedWordsConfig(["bad", "words"])
    config.remove_word("bad")
    assert "bad" not in config.get_prohibited_words()

def test_remove_nonexistent_word():
    """Test that removing a non-existent word raises KeyError."""
    config = ProhibitedWordsConfig(["bad"])
    with pytest.raises(KeyError):
        config.remove_word("good")

def test_add_empty_word():
    """Test that adding an empty word raises ValueError."""
    config = ProhibitedWordsConfig()
    with pytest.raises(ValueError):
        config.add_word("")
    with pytest.raises(ValueError):
        config.add_word("   ")

def test_check_text_positive():
    """Test checking text for prohibited words."""
    config = ProhibitedWordsConfig(["bad", "terrible"])
    assert config.check_text("This is a bad word")
    assert config.check_text("Terrible sentence here")
    assert config.check_text("BAD WORD in uppercase")

def test_check_text_negative():
    """Test checking text without prohibited words."""
    config = ProhibitedWordsConfig(["bad", "terrible"])
    assert not config.check_text("This is a good sentence")
    assert not config.check_text("")
    assert not config.check_text(None)

def test_get_prohibited_words():
    """Test retrieving the list of prohibited words."""
    config = ProhibitedWordsConfig(["bad", "Terrible"])
    words = config.get_prohibited_words()
    assert set(words) == {"bad", "terrible"}
    assert len(words) == 2