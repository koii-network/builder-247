"""
Content Filtering Utility Module

This module provides functionality for filtering content based on specified criteria.
"""

import re
from typing import List, Union, Optional


class ContentFilter:
    """
    A utility class for filtering content based on various criteria.
    """

    @staticmethod
    def filter_by_keywords(
        content: str, 
        keywords: List[str], 
        mode: str = 'exclude', 
        case_sensitive: bool = False
    ) -> Optional[str]:
        """
        Filter content based on specified keywords.

        Args:
            content (str): The text to filter
            keywords (List[str]): List of keywords to filter by
            mode (str, optional): Filtering mode. 
                'exclude' removes content containing keywords
                'include' keeps only content with keywords
                Defaults to 'exclude'
            case_sensitive (bool, optional): Whether filtering is case-sensitive. 
                Defaults to False.

        Returns:
            Optional[str]: Filtered content or None if entire content is filtered out

        Raises:
            ValueError: If an invalid mode is provided
        """
        if not content or not keywords:
            return content

        # Validate mode
        if mode not in ['exclude', 'include']:
            raise ValueError("Mode must be either 'exclude' or 'include'")

        # Prepare for matching
        search_content = content.lower() if not case_sensitive else content
        search_keywords = [kw.lower() if not case_sensitive else kw for kw in keywords]

        # Filter logic
        if mode == 'exclude':
            # Remove content if any keyword is found
            for keyword in search_keywords:
                if keyword in search_content:
                    return None
            return content
        else:  # mode == 'include'
            # Keep content only if any keyword is found
            for keyword in search_keywords:
                if keyword in search_content:
                    return content
            return None

    @staticmethod
    def remove_patterns(
        content: str, 
        patterns: List[str], 
        flags: int = 0
    ) -> str:
        """
        Remove content matching specified regex patterns.

        Args:
            content (str): The text to process
            patterns (List[str]): List of regex patterns to remove
            flags (int, optional): Regex flags. Defaults to 0.

        Returns:
            str: Content with matched patterns removed
        """
        if not content or not patterns:
            return content

        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=flags)

        return content.strip()

    @staticmethod
    def mask_sensitive_info(
        content: str, 
        mask_patterns: Optional[List[str]] = None
    ) -> str:
        """
        Mask sensitive information in the content.

        Args:
            content (str): The text to process
            mask_patterns (Optional[List[str]], optional): Custom regex patterns 
                to mask. Defaults to some standard patterns if None.

        Returns:
            str: Content with sensitive information masked
        """
        # Default sensitive information patterns if none provided
        if mask_patterns is None:
            mask_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP Address
                r'\b\d{16,19}\b',  # Credit Card Number
                r'\b\d{3}-\d{2}-\d{4}\b'  # SSN
            ]

        # Replace matched patterns with [MASKED]
        for pattern in mask_patterns:
            content = re.sub(pattern, '[MASKED]', content)

        return content