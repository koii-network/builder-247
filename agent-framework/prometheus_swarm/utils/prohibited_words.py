"""
Prohibited Words Configuration Module

This module provides a configuration mechanism for managing and checking prohibited words
across different contexts in the Prometheus Swarm framework.
"""

import re
from typing import List, Optional, Set, Union


class ProhibitedWordsConfig:
    """
    A configuration class for managing prohibited words with support for context-specific filtering.
    
    Attributes:
        global_prohibited_words (Set[str]): A set of words prohibited across all contexts.
    """

    def __init__(self, global_words: Optional[Union[List[str], Set[str]]] = None):
        """
        Initialize the ProhibitedWordsConfig with optional global prohibited words.

        Args:
            global_words (Optional[Union[List[str], Set[str]]], optional): 
                A list or set of global prohibited words. Defaults to None.
        """
        self.global_prohibited_words = set(word.lower() for word in (global_words or []))
        self._context_prohibited_words: dict[str, set[str]] = {}

    def add_global_prohibited_word(self, word: str) -> None:
        """
        Add a word to the global prohibited words list.

        Args:
            word (str): The word to be added to global prohibited words.
        """
        self.global_prohibited_words.add(word.lower())

    def add_context_prohibited_words(self, context: str, words: Union[List[str], Set[str]]) -> None:
        """
        Add prohibited words for a specific context.

        Args:
            context (str): The context identifier.
            words (Union[List[str], Set[str]]): Words to be prohibited in the specific context.
        """
        context_words = set(word.lower() for word in words)
        self._context_prohibited_words[context] = context_words

    def get_context_prohibited_words(self, context: str) -> Set[str]:
        """
        Retrieve prohibited words for a specific context.

        Args:
            context (str): The context identifier.

        Returns:
            Set[str]: A set of prohibited words for the given context.
        """
        return self._context_prohibited_words.get(context, set())

    def is_prohibited(self, text: str, context: Optional[str] = None) -> bool:
        """
        Check if the given text contains any prohibited words.

        Args:
            text (str): The text to check for prohibited words.
            context (Optional[str], optional): An optional context to check context-specific words.

        Returns:
            bool: True if the text contains a prohibited word, False otherwise.
        """
        # Convert text to lowercase for case-insensitive matching
        lower_text = text.lower()

        # Check global prohibited words
        for word in self.global_prohibited_words:
            if _word_in_text(word, lower_text):
                return True

        # Check context-specific prohibited words if context is provided
        if context and context in self._context_prohibited_words:
            for word in self._context_prohibited_words[context]:
                if _word_in_text(word, lower_text):
                    return True

        return False

    def get_prohibited_words(self, text: str, context: Optional[str] = None) -> Set[str]:
        """
        Retrieve the list of prohibited words found in the text.

        Args:
            text (str): The text to check for prohibited words.
            context (Optional[str], optional): An optional context to check context-specific words.

        Returns:
            Set[str]: A set of prohibited words found in the text.
        """
        # Convert text to lowercase for case-insensitive matching
        lower_text = text.lower()
        found_prohibited_words = set()

        # Check global prohibited words
        found_prohibited_words.update(
            word for word in self.global_prohibited_words if _word_in_text(word, lower_text)
        )

        # Check context-specific prohibited words if context is provided
        if context and context in self._context_prohibited_words:
            context_words = self._context_prohibited_words[context]
            found_prohibited_words.update(
                word for word in context_words if _word_in_text(word, lower_text)
            )

        return found_prohibited_words


def _word_in_text(word: str, text: str) -> bool:
    """
    Check if a word is present in the text as a whole word (with word boundaries).

    Args:
        word (str): The word to search for.
        text (str): The text to search in.

    Returns:
        bool: True if the word is found as a whole word, False otherwise.
    """
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))