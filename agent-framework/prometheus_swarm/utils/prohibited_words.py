"""
Module for managing prohibited words configuration.

This module provides functionality to define, check, and manage 
a list of prohibited words that can be used to filter content.
"""

class ProhibitedWordsConfig:
    """
    A configuration class for managing prohibited words.
    
    Attributes:
        _prohibited_words (set): A set of prohibited words in lowercase.
    """
    
    def __init__(self, initial_words=None):
        """
        Initialize the prohibited words configuration.
        
        Args:
            initial_words (list, optional): Initial list of prohibited words. 
                Defaults to None.
        """
        self._prohibited_words = set(
            word.lower() for word in (initial_words or [])
        )
    
    def add_word(self, word):
        """
        Add a word to the prohibited words list.
        
        Args:
            word (str): The word to prohibit.
        
        Raises:
            ValueError: If the word is empty or contains whitespace.
        """
        if not word or not word.strip():
            raise ValueError("Prohibited word cannot be empty or whitespace.")
        
        self._prohibited_words.add(word.lower())
    
    def remove_word(self, word):
        """
        Remove a word from the prohibited words list.
        
        Args:
            word (str): The word to remove.
        
        Raises:
            KeyError: If the word is not in the prohibited words list.
        """
        lowercase_word = word.lower()
        if lowercase_word not in self._prohibited_words:
            raise KeyError(f"Word '{word}' not found in prohibited words.")
        
        self._prohibited_words.remove(lowercase_word)
    
    def check_text(self, text):
        """
        Check if the given text contains any prohibited words.
        
        Args:
            text (str): The text to check.
        
        Returns:
            bool: True if prohibited words are found, False otherwise.
        """
        if not text:
            return False
        
        # Split text into words, convert to lowercase for case-insensitive check
        words = text.lower().split()
        return any(word in self._prohibited_words for word in words)
    
    def get_prohibited_words(self):
        """
        Get the current list of prohibited words.
        
        Returns:
            list: A list of prohibited words.
        """
        return list(self._prohibited_words)