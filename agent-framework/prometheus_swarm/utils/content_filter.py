"""
Content Filtering Utility

This module provides functionality for filtering and sanitizing content 
based on configurable rules and criteria.
"""

import re
from typing import List, Union, Optional


class ContentFilter:
    """
    A utility class for filtering and sanitizing content.
    
    Supports filtering based on:
    - Blacklisted words/phrases
    - Regular expression patterns
    - Maximum content length
    - Specific content types
    """
    
    def __init__(
        self, 
        blacklist: Optional[List[str]] = None, 
        max_length: Optional[int] = None, 
        allowed_chars_regex: Optional[str] = None
    ):
        """
        Initialize the content filter with optional filtering rules.
        
        Args:
            blacklist (Optional[List[str]]): List of prohibited words/phrases
            max_length (Optional[int]): Maximum allowed content length
            allowed_chars_regex (Optional[str]): Regex pattern for allowed characters
        """
        self.blacklist = blacklist or []
        self.max_length = max_length
        self.allowed_chars_regex = allowed_chars_regex
    
    def sanitize(self, content: str) -> str:
        """
        Sanitize the given content based on configured rules.
        
        Args:
            content (str): The content to sanitize
        
        Returns:
            str: Sanitized content
        
        Raises:
            ValueError: If content fails validation
        """
        # Check content length
        if self.max_length and len(content) > self.max_length:
            raise ValueError(f"Content exceeds maximum length of {self.max_length}")
        
        # Check for blacklisted words
        for word in self.blacklist:
            if word.lower() in content.lower():
                raise ValueError(f"Content contains blacklisted word: {word}")
        
        # Filter using allowed characters regex if specified
        if self.allowed_chars_regex:
            # Use re.fullmatch instead of re.match to ensure whole string match
            if not re.fullmatch(self.allowed_chars_regex, content):
                raise ValueError("Content contains disallowed characters")
        
        return content
    
    def contains_sensitive_content(self, content: str) -> bool:
        """
        Check if content contains sensitive information.
        
        Args:
            content (str): Content to check
        
        Returns:
            bool: True if sensitive content is detected, False otherwise
        """
        # Check for blacklisted words
        for word in self.blacklist:
            if word.lower() in content.lower():
                return True
        
        return False
    
    def redact(self, content: str, replacement: str = '[REDACTED]') -> str:
        """
        Redact sensitive content based on blacklist.
        
        Args:
            content (str): Content to redact
            replacement (str, optional): Replacement text. Defaults to '[REDACTED]'
        
        Returns:
            str: Redacted content
        """
        redacted_content = content
        for word in self.blacklist:
            redacted_content = re.sub(
                word, 
                replacement, 
                redacted_content, 
                flags=re.IGNORECASE
            )
        
        return redacted_content