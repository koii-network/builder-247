"""
Prohibited Words Configuration Module

This module provides functionality to manage and check for prohibited words.
"""

from typing import List, Union


class ProhibitedWordsConfig:
    """
    A configuration class for managing prohibited words.
    """

    def __init__(self, prohibited_words: Union[List[str], None] = None):
        """
        Initialize the ProhibitedWordsConfig.

        Args:
            prohibited_words (List[str], optional): A list of prohibited words.
                Defaults to None, which means an empty list.
        """
        self._prohibited_words = [
            word.lower() for word in (prohibited_words or [])
        ]

    def add_prohibited_word(self, word: str) -> None:
        """
        Add a new prohibited word to the configuration.

        Args:
            word (str): The word to prohibit.
        """
        normalized_word = word.lower()
        if normalized_word not in self._prohibited_words:
            self._prohibited_words.append(normalized_word)

    def remove_prohibited_word(self, word: str) -> None:
        """
        Remove a word from the prohibited words list.

        Args:
            word (str): The word to remove from prohibited words.
        """
        normalized_word = word.lower()
        if normalized_word in self._prohibited_words:
            self._prohibited_words.remove(normalized_word)

    def get_prohibited_words(self) -> List[str]:
        """
        Retrieve the current list of prohibited words.

        Returns:
            List[str]: A list of prohibited words.
        """
        return self._prohibited_words.copy()

    def contains_prohibited_words(self, text: str) -> bool:
        """
        Check if the given text contains any prohibited words.

        Args:
            text (str): The text to check for prohibited words.

        Returns:
            bool: True if prohibited words are found, False otherwise.
        """
        if not text:
            return False

        # Normalize text to lowercase and split into words
        text_words = text.lower().split()

        # Check if any prohibited word is in the text
        return any(word in text_words for word in self._prohibited_words)

    def replace_prohibited_words(self, text: str, replacement: str = '[REDACTED]') -> str:
        """
        Replace prohibited words in the text with a replacement word.

        Args:
            text (str): The text to process.
            replacement (str, optional): Word to replace prohibited words.
                Defaults to '[REDACTED]'.

        Returns:
            str: The processed text with prohibited words replaced.
        """
        if not text:
            return text

        # Split text into words
        words = text.split()

        # Replace prohibited words
        processed_words = [
            replacement if word.lower() in self._prohibited_words else word
            for word in words
        ]

        return ' '.join(processed_words)