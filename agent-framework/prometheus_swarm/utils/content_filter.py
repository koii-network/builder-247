"""
Content Filtering Utility Module

This module provides functionality for filtering content based on various criteria.
"""

import re
from typing import List, Union, Optional, Callable


class ContentFilter:
    """
    A utility class for filtering content based on various criteria.
    
    Supports filtering by:
    - Banned words
    - Content length
    - Custom regex patterns
    - Custom filter functions
    """

    def __init__(
        self, 
        banned_words: Optional[List[str]] = None, 
        min_length: Optional[int] = None, 
        max_length: Optional[int] = None
    ):
        """
        Initialize a ContentFilter instance.
        
        Args:
            banned_words (List[str], optional): List of words to ban. Defaults to None.
            min_length (int, optional): Minimum allowed content length. Defaults to None.
            max_length (int, optional): Maximum allowed content length. Defaults to None.
        """
        self.banned_words = [word.lower() for word in (banned_words or [])]
        self.min_length = min_length
        self.max_length = max_length

    def add_banned_word(self, word: str) -> None:
        """
        Add a banned word to the filter.
        
        Args:
            word (str): Word to ban.
        """
        self.banned_words.append(word.lower())

    def filter_content(
        self, 
        content: str, 
        custom_regex: Optional[List[str]] = None, 
        custom_filter: Optional[Callable[[str], bool]] = None
    ) -> Union[str, None]:
        """
        Filter content based on configured criteria.
        
        Args:
            content (str): Content to filter
            custom_regex (List[str], optional): Additional regex patterns to match. Defaults to None.
            custom_filter (Callable, optional): Custom filter function. Defaults to None.
        
        Returns:
            Union[str, None]: Filtered content or None if content is rejected
        """
        # Validate input
        if not isinstance(content, str):
            raise TypeError("Content must be a string")

        # Check length constraints
        if self.min_length is not None and len(content) < self.min_length:
            return None
        
        if self.max_length is not None and len(content) > self.max_length:
            return None

        # Check for banned words
        content_lower = content.lower()
        for word in self.banned_words:
            if word in content_lower:
                return None

        # Check custom regex patterns
        if custom_regex:
            for pattern in custom_regex:
                if re.search(pattern, content):
                    return None

        # Apply custom filter function
        if custom_filter and not custom_filter(content):
            return None

        return content