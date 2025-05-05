"""
Unit tests for the ProhibitedWordsConfig utility.
"""

import pytest
from prometheus_swarm.utils.prohibited_words import ProhibitedWordsConfig


def test_initialize_empty_config():
    """Test initialization of ProhibitedWordsConfig with no initial words."""
    config = ProhibitedWordsConfig()
    assert len(config.get_prohibited_words()) == 0


def test_initialize_with_words():
    """Test initialization of ProhibitedWordsConfig with initial words."""
    config = ProhibitedWordsConfig(["bad", "inappropriate"])
    prohibited_words = config.get_prohibited_words()
    assert "bad" in prohibited_words
    assert "inappropriate" in prohibited_words


def test_add_words():
    """Test adding words to the prohibited words config."""
    config = ProhibitedWordsConfig()
    config.add_words(["spam", "toxic"])
    prohibited_words = config.get_prohibited_words()
    assert "spam" in prohibited_words
    assert "toxic" in prohibited_words


def test_remove_words():
    """Test removing words from the prohibited words config."""
    config = ProhibitedWordsConfig(["remove", "delete"])
    config.remove_words(["remove"])
    prohibited_words = config.get_prohibited_words()
    assert "remove" not in prohibited_words
    assert "delete" in prohibited_words


def test_check_text_with_prohibited_words():
    """Test checking text for prohibited words."""
    config = ProhibitedWordsConfig(["bad", "inappropriate"])
    assert config.check_text("This is a bad comment")
    assert config.check_text("Inappropriate language used here")
    assert config.check_text("BAD words in CAPS")
    assert config.check_text("This bad! word is not okay.")


def test_check_text_without_prohibited_words():
    """Test checking text without prohibited words."""
    config = ProhibitedWordsConfig(["bad", "inappropriate"])
    assert not config.check_text("This is a good comment")
    assert not config.check_text("Entirely acceptable language")


def test_check_text_with_punctuation():
    """Test checking text with various punctuation and special characters."""
    config = ProhibitedWordsConfig(["bad", "inappropriate"])
    assert config.check_text("This is a bad! comment.")
    assert config.check_text("Inappropriate, language here.")


def test_check_text_with_empty_input():
    """Test checking empty text."""
    config = ProhibitedWordsConfig(["bad"])
    assert not config.check_text("")
    assert not config.check_text(None)


def test_word_normalization():
    """Test word normalization in prohibited words config."""
    config = ProhibitedWordsConfig(["Bad!", "Inappropriate."])
    prohibited_words = config.get_prohibited_words()
    assert "bad" in prohibited_words
    assert "inappropriate" in prohibited_words