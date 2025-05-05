"""
Tests for the Content Filtering Utility
"""

import pytest
from prometheus_swarm.utils.content_filter import ContentFilter


def test_content_filter_init():
    """Test initialization of ContentFilter."""
    cf = ContentFilter(
        banned_words=['bad', 'wrong'], 
        min_length=5, 
        max_length=100
    )
    assert cf.banned_words == ['bad', 'wrong']
    assert cf.min_length == 5
    assert cf.max_length == 100


def test_content_filter_add_banned_word():
    """Test adding a banned word to the filter."""
    cf = ContentFilter()
    cf.add_banned_word('danger')
    assert 'danger' in cf.banned_words


def test_content_filter_pass_basic_filter():
    """Test basic content filtering with valid content."""
    cf = ContentFilter()
    result = cf.filter_content("This is a good content")
    assert result == "This is a good content"


def test_content_filter_reject_banned_words():
    """Test rejection of content with banned words."""
    cf = ContentFilter(banned_words=['bad', 'wrong'])
    result = cf.filter_content("This is a bad example")
    assert result is None
    result = cf.filter_content("This is a WRONG example")
    assert result is None


def test_content_filter_length_constraints():
    """Test content length filtering."""
    cf = ContentFilter(min_length=10, max_length=20)
    
    # Test content too short
    result = cf.filter_content("Short")
    assert result is None
    
    # Test content too long
    result = cf.filter_content("This is a very long content that exceeds the max length")
    assert result is None
    
    # Test content within length
    result = cf.filter_content("Just right")
    assert result == "Just right"


def test_content_filter_custom_regex():
    """Test filtering with custom regex."""
    cf = ContentFilter()
    result = cf.filter_content(
        "This is a test", 
        custom_regex=[r'\btest\b']
    )
    assert result is None

    result = cf.filter_content(
        "This is good", 
        custom_regex=[r'\btest\b']
    )
    assert result == "This is good"


def test_content_filter_custom_function():
    """Test filtering with a custom function."""
    def custom_filter(content):
        return 'good' in content

    cf = ContentFilter()
    result = cf.filter_content(
        "This is amazing", 
        custom_filter=custom_filter
    )
    assert result is None

    result = cf.filter_content(
        "This is a good example", 
        custom_filter=custom_filter
    )
    assert result == "This is a good example"


def test_content_filter_type_error():
    """Test that non-string inputs raise TypeError."""
    cf = ContentFilter()
    with pytest.raises(TypeError):
        cf.filter_content(123)
    with pytest.raises(TypeError):
        cf.filter_content(None)


def test_case_insensitive_banned_words():
    """Test that banned words are case-insensitive."""
    cf = ContentFilter(banned_words=['bad'])
    result = cf.filter_content("This is a BAD example")
    assert result is None