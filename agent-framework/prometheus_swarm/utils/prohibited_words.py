"""
Module for managing prohibited words configuration.

This module provides functionality to:
1. Define and manage a list of prohibited words
2. Check if text contains any prohibited words
3. Configure prohibited words from various sources
"""

import re
from typing import List, Union


class ProhibitedWordsConfig:
    """
    Manages configuration and checking of prohibited words.
    
    Attributes:
        _prohibited_words (set): A set of normalized prohibited words
    """

    def __init__(self, initial_words: Union[List[str], None] = None):
        """
        Initialize the ProhibitedWordsConfig.

        Args:
            initial_words (List[str], optional): Initial list of prohibited words. Defaults to None.
        """
        self._prohibited_words = set()
        if initial_words:
            self.add_words(initial_words)

    def add_words(self, words: List[str]) -> None:
        """
        Add words to the prohibited words list.

        Args:
            words (List[str]): List of words to add to prohibited words.
        """
        normalized_words = [self._normalize_word(word) for word in words]
        self._prohibited_words.update(normalized_words)

    def remove_words(self, words: List[str]) -> None:
        """
        Remove words from the prohibited words list.

        Args:
            words (List[str]): List of words to remove from prohibited words.
        """
        normalized_words = [self._normalize_word(word) for word in words]
        self._prohibited_words.difference_update(normalized_words)

    def check_text(self, text: str) -> bool:
        """
        Check if the given text contains any prohibited words.

        Args:
            text (str): Text to check for prohibited words.

        Returns:
            bool: True if text contains prohibited words, False otherwise.
        """
        if not text:
            return False

        normalized_text = self._normalize_word(text)
        words = re.findall(r'\b\w+\b', normalized_text)

        return any(word in self._prohibited_words for word in words)

    @staticmethod
    def _normalize_word(word: str) -> str:
        """
        Normalize a word by converting to lowercase and removing non-alphanumeric characters.

        Args:
            word (str): Word to normalize.

        Returns:
            str: Normalized word.
        """
        return re.sub(r'[^a-z0-9]', '', word.lower())

    def get_prohibited_words(self) -> List[str]:
        """
        Get the current list of prohibited words.

        Returns:
            List[str]: List of currently configured prohibited words.
        """
        return list(self._prohibited_words)