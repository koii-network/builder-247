"""
Unit tests for the ProhibitedWordsConfig class.
"""

import pytest
from prometheus_swarm.utils.prohibited_words import ProhibitedWordsConfig


def test_global_prohibited_words_initialization():
    """Test initialization with global prohibited words."""
    global_words = ["badword1", "badword2"]
    config = ProhibitedWordsConfig(global_words)
    
    assert config.global_prohibited_words == {"badword1", "badword2"}


def test_add_global_prohibited_word():
    """Test adding a global prohibited word."""
    config = ProhibitedWordsConfig()
    config.add_global_prohibited_word("secretword")
    
    assert "secretword" in config.global_prohibited_words


def test_add_context_prohibited_words():
    """Test adding prohibited words to a specific context."""
    config = ProhibitedWordsConfig()
    context_words = ["contextword1", "contextword2"]
    
    config.add_context_prohibited_words("code_review", context_words)
    context_prohibited = config.get_context_prohibited_words("code_review")
    
    assert context_prohibited == {"contextword1", "contextword2"}


def test_is_prohibited_global():
    """Test detecting prohibited words across global context."""
    config = ProhibitedWordsConfig(["badword"])
    
    assert config.is_prohibited("This is a badword sentence")
    assert not config.is_prohibited("This is a good sentence")


def test_is_prohibited_context():
    """Test detecting prohibited words in a specific context."""
    config = ProhibitedWordsConfig()
    config.add_context_prohibited_words("pr_review", ["harmful", "inappropriate"])
    
    assert config.is_prohibited("Harmful content", context="pr_review")
    assert not config.is_prohibited("Good content", context="pr_review")


def test_is_prohibited_case_insensitive():
    """Test case-insensitive prohibited word detection."""
    config = ProhibitedWordsConfig(["secret"])
    
    assert config.is_prohibited("This contains a SECRET word")
    assert config.is_prohibited("SECRET at the beginning")
    assert config.is_prohibited("word at the end is SECRET")


def test_get_prohibited_words():
    """Test retrieving the list of prohibited words in text."""
    config = ProhibitedWordsConfig(["global", "banned"])
    config.add_context_prohibited_words("custom", ["custom_bad"])
    
    global_prohibited = config.get_prohibited_words("This is a global bad text")
    assert global_prohibited == {"global"}
    
    context_prohibited = config.get_prohibited_words("custom bad word", context="custom")
    assert context_prohibited == {"custom_bad"}
    
    mixed_prohibited = config.get_prohibited_words("Global and custom_bad mixed", context="custom")
    assert mixed_prohibited == {"global", "custom_bad"}


def test_empty_configuration():
    """Test behavior with empty configuration."""
    config = ProhibitedWordsConfig()
    
    assert not config.is_prohibited("Some text")
    assert config.get_prohibited_words("Some text") == set()


def test_multiple_context_configuration():
    """Test multiple different context configurations."""
    config = ProhibitedWordsConfig(["global_bad"])
    config.add_context_prohibited_words("context1", ["bad1"])
    config.add_context_prohibited_words("context2", ["bad2"])
    
    assert config.is_prohibited("bad1 text", context="context1")
    assert config.is_prohibited("bad2 text", context="context2")
    assert not config.is_prohibited("bad1 text", context="context2")