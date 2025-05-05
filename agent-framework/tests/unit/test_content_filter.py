"""
Unit tests for Content Filtering Utility
"""

import pytest
from prometheus_swarm.utils.content_filter import ContentFilter


class TestContentFilter:
    def test_filter_by_keywords_exclude(self):
        # Test excluding content with keywords
        content = "Hello world, this is a test"
        
        # Should return None when keyword is present
        assert ContentFilter.filter_by_keywords(content, ['test']) is None
        
        # Should return content when keyword is not present
        assert ContentFilter.filter_by_keywords(content, ['secret']) == content

    def test_filter_by_keywords_include(self):
        # Test including content with keywords
        content = "Hello world, this is a test"
        
        # Should return content when keyword is present
        assert ContentFilter.filter_by_keywords(content, ['test'], mode='include') == content
        
        # Should return None when keyword is not present
        assert ContentFilter.filter_by_keywords(content, ['secret'], mode='include') is None

    def test_filter_by_keywords_case_sensitive(self):
        content = "Hello World"
        
        # Case-sensitive should distinguish between cases
        assert ContentFilter.filter_by_keywords(content, ['world'], case_sensitive=True) == content
        assert ContentFilter.filter_by_keywords(content, ['World'], case_sensitive=True) is None

    def test_filter_by_keywords_invalid_mode(self):
        with pytest.raises(ValueError):
            ContentFilter.filter_by_keywords("test", ['keyword'], mode='invalid')

    def test_remove_patterns(self):
        content = "Hello 123-45-6789 world"
        
        # Remove specific pattern
        filtered = ContentFilter.remove_patterns(content, [r'\d{3}-\d{2}-\d{4}'])
        assert filtered == "Hello  world"

    def test_mask_sensitive_info(self):
        content = "Contact me at john.doe@example.com or 123-45-6789"
        
        masked = ContentFilter.mask_sensitive_info(content)
        assert masked == "Contact me at [MASKED] or [MASKED]"

    def test_mask_sensitive_info_custom_patterns(self):
        content = "Secret code: ABCDEF1234567890"
        
        # Mask with custom pattern
        masked = ContentFilter.mask_sensitive_info(content, [r'[A-Z]+\d+'])
        assert masked == "Secret code: [MASKED]"

    def test_empty_input(self):
        # Test various methods with empty input
        assert ContentFilter.filter_by_keywords("", ['test']) == ""
        assert ContentFilter.remove_patterns("", [r'\d+']) == ""
        assert ContentFilter.mask_sensitive_info("") == ""