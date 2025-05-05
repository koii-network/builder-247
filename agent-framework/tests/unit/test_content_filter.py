"""
Unit tests for the Content Filtering Utility
"""

import pytest
from prometheus_swarm.utils.content_filter import ContentFilter


def test_content_filter_initialization():
    """Test initialization of ContentFilter with various parameters."""
    filter1 = ContentFilter()
    assert filter1.blacklist == []
    assert filter1.max_length is None
    assert filter1.allowed_chars_regex is None

    blacklist = ['bad', 'word']
    filter2 = ContentFilter(
        blacklist=blacklist, 
        max_length=100, 
        allowed_chars_regex=r'\w+'
    )
    assert filter2.blacklist == blacklist
    assert filter2.max_length == 100
    assert filter2.allowed_chars_regex == r'\w+'


def test_content_sanitization_success():
    """Test successful content sanitization."""
    filter_obj = ContentFilter(
        blacklist=['secret', 'private'], 
        max_length=50,
        allowed_chars_regex=r'[a-zA-Z0-9\s]+'
    )

    # Test valid content passes
    assert filter_obj.sanitize("This is a normal message") == "This is a normal message"
    assert filter_obj.sanitize("Valid123 content") == "Valid123 content"


def test_content_sanitization_failures():
    """Test content sanitization failures."""
    filter_obj = ContentFilter(
        blacklist=['secret', 'private'], 
        max_length=50,
        allowed_chars_regex=r'[a-zA-Z0-9\s]+'
    )

    # Test blacklisted words
    with pytest.raises(ValueError, match="Content contains blacklisted word: secret"):
        filter_obj.sanitize("This contains a secret message")

    # Test maximum length
    with pytest.raises(ValueError, match="Content exceeds maximum length"):
        filter_obj.sanitize("This is a very long message that exceeds the maximum allowed length")

    # Test disallowed characters
    with pytest.raises(ValueError, match="Content contains disallowed characters"):
        filter_obj.sanitize("Invalid@content")


def test_sensitive_content_detection():
    """Test detection of sensitive content."""
    filter_obj = ContentFilter(blacklist=['secret', 'private'])

    # Test sensitive content detection
    assert filter_obj.contains_sensitive_content("This contains a secret message") == True
    assert filter_obj.contains_sensitive_content("This is a normal message") == False
    
    # Test case-insensitive detection
    assert filter_obj.contains_sensitive_content("This contains a SECRET message") == True


def test_content_redaction():
    """Test content redaction functionality."""
    filter_obj = ContentFilter(blacklist=['secret', 'private'])

    # Test redaction
    assert filter_obj.redact("This contains a secret message") == "This contains a [REDACTED] message"
    assert filter_obj.redact("This contains a PRIVATE thing", replacement='XXX') == "This contains a XXX thing"
    
    # Test multiple redactions
    assert (filter_obj.redact("secret private message") 
            == "[REDACTED] [REDACTED] message")


def test_mixed_case_redaction():
    """Test redaction with mixed case sensitivity."""
    filter_obj = ContentFilter(blacklist=['secret', 'private'])

    # Test case-insensitive redaction
    assert filter_obj.redact("This contains a Secret message") == "This contains a [REDACTED] message"
    assert filter_obj.redact("PRIVATE information here") == "[REDACTED] information here"