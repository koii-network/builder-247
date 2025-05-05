"""
Unit tests for the ProhibitedWordsConfig class.
"""

import pytest
from prometheus_swarm.config.prohibited_words import ProhibitedWordsConfig


def test_initialize_empty_config():
    """Test initializing a config with no initial words."""
    config = ProhibitedWordsConfig()
    assert len(config.get_prohibited_words()) == 0


def test_initialize_with_initial_words():
    """Test initializing a config with initial words."""
    initial_words = ["bad", "wrong", "inappropriate"]
    config = ProhibitedWordsConfig(initial_words)
    assert set(config.get_prohibited_words()) == set(initial_words)


def test_add_word():
    """Test adding a word to the prohibited words list."""
    config = ProhibitedWordsConfig()
    config.add_word("offensive")
    assert "offensive" in config.get_prohibited_words()


def test_add_word_case_insensitive():
    """Test that words are added case-insensitively."""
    config = ProhibitedWordsConfig()
    config.add_word("Offensive")
    config.add_word("offensive")
    assert len(config.get_prohibited_words()) == 1


def test_add_word_strips_whitespace():
    """Test that words are stripped of leading/trailing whitespace."""
    config = ProhibitedWordsConfig()
    config.add_word("  bad  ")
    assert "bad" in config.get_prohibited_words()


def test_add_empty_word_raises_error():
    """Test that adding an empty word raises a ValueError."""
    config = ProhibitedWordsConfig()
    with pytest.raises(ValueError):
        config.add_word("")
    with pytest.raises(ValueError):
        config.add_word("   ")


def test_remove_word():
    """Test removing a word from the prohibited words list."""
    config = ProhibitedWordsConfig(["bad", "wrong"])
    config.remove_word("bad")
    assert "bad" not in config.get_prohibited_words()
    assert "wrong" in config.get_prohibited_words()


def test_check_text_with_prohibited_words():
    """Test checking text for prohibited words."""
    config = ProhibitedWordsConfig(["bad", "wrong"])
    
    # Text containing prohibited words
    assert config.check_text("this is a bad example") == True
    assert config.check_text("something WRONG happened") == True
    
    # Text without prohibited words
    assert config.check_text("this is a good example") == False


def test_check_text_edge_cases():
    """Test checking text with various edge cases."""
    config = ProhibitedWordsConfig(["bad"])
    
    # Empty text
    assert config.check_text("") == False
    
    # Partial word matches
    assert config.check_text("badword") == False
    assert config.check_text("bad word") == True