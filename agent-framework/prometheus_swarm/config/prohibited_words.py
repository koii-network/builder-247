"""
Module for managing prohibited words configuration.

This module provides functionality to define, validate, and check against 
a list of prohibited words.
"""

from typing import List, Union


class ProhibitedWordsConfig:
    """
    A configuration class for managing prohibited words.
    
    Allows adding, removing, and checking words against a prohibited list.
    """
    
    def __init__(self, initial_words: Union[List[str], None] = None):
        """
        Initialize the prohibited words configuration.
        
        Args:
            initial_words (list, optional): Initial list of prohibited words. 
                                            Defaults to None.
        """
        self._prohibited_words = set(initial_words or [])
    
    def add_word(self, word: str) -> None:
        """
        Add a word to the prohibited words list.
        
        Args:
            word (str): The word to add to the prohibited list.
        
        Raises:
            ValueError: If the word is empty or contains only whitespace.
        """
        if not word or word.isspace():
            raise ValueError("Prohibited word cannot be empty or whitespace")
        
        # Convert to lowercase to ensure case-insensitive matching
        self._prohibited_words.add(word.lower().strip())
    
    def remove_word(self, word: str) -> None:
        """
        Remove a word from the prohibited words list.
        
        Args:
            word (str): The word to remove from the prohibited list.
        """
        self._prohibited_words.discard(word.lower().strip())
    
    def check_text(self, text: str) -> bool:
        """
        Check if the given text contains any prohibited words.
        
        Args:
            text (str): The text to check for prohibited words.
        
        Returns:
            bool: True if any prohibited words are found, False otherwise.
        """
        if not text:
            return False
        
        # Convert text to lowercase and split into words
        words = text.lower().split()
        
        # Check if any word matches a prohibited word
        return any(word in self._prohibited_words for word in words)
    
    def get_prohibited_words(self) -> List[str]:
        """
        Retrieve the current list of prohibited words.
        
        Returns:
            list: A list of prohibited words.
        """
        return list(self._prohibited_words)