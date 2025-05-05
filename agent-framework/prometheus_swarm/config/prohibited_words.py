"""
Module for managing prohibited words configuration.

This module provides functionality to define and check against a list of prohibited words
to prevent sensitive or inappropriate content.
"""

from typing import List, Union


class ProhibitedWordsConfig:
    """
    A configuration class for managing prohibited words.

    This class allows defining a set of prohibited words and provides methods
    to check text against these words.
    """

    def __init__(self, prohibited_words: Union[List[str], None] = None):
        """
        Initialize the prohibited words configuration.

        Args:
            prohibited_words (List[str], optional): A list of words to prohibit.
                If None, defaults to an empty list. Defaults to None.
        """
        self._prohibited_words = set(
            word.lower().strip() for word in (prohibited_words or [])
        )

    def add_prohibited_word(self, word: str) -> None:
        """
        Add a single word to the prohibited words list.

        Args:
            word (str): The word to add to the prohibited list.
        """
        self._prohibited_words.add(word.lower().strip())

    def add_prohibited_words(self, words: List[str]) -> None:
        """
        Add multiple words to the prohibited words list.

        Args:
            words (List[str]): A list of words to add to the prohibited list.
        """
        self._prohibited_words.update(word.lower().strip() for word in words)

    def check_text(self, text: str) -> bool:
        """
        Check if the given text contains any prohibited words.

        Args:
            text (str): The text to check for prohibited words.

        Returns:
            bool: True if no prohibited words are found, False otherwise.
        """
        if not self._prohibited_words:
            return True

        # Convert text to lowercase and split into words
        words = text.lower().split()
        
        # Check if any prohibited words are in the text
        return all(word not in self._prohibited_words for word in words)

    @property
    def prohibited_words(self) -> List[str]:
        """
        Get the current list of prohibited words.

        Returns:
            List[str]: A list of prohibited words.
        """
        return list(self._prohibited_words)