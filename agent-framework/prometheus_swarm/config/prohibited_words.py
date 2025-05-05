"""
Module for managing prohibited words configuration and validation.
"""
from typing import List, Union

class ProhibitedWordsConfig:
    """
    Configuration and validation class for prohibited words.
    """
    def __init__(self, prohibited_words: Union[List[str], None] = None):
        """
        Initialize the prohibited words configuration.

        Args:
            prohibited_words (List[str], optional): List of words to prohibit. 
                Defaults to None.
        """
        self.prohibited_words = prohibited_words or []
        # Convert all words to lowercase for case-insensitive matching
        self.prohibited_words = [word.lower() for word in self.prohibited_words]

    def is_text_prohibited(self, text: str) -> bool:
        """
        Check if the given text contains any prohibited words.

        Args:
            text (str): Text to validate.

        Returns:
            bool: True if text contains prohibited words, False otherwise.
        """
        if not text or not self.prohibited_words:
            return False

        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()

        # Check if any prohibited word is in the text
        return any(word in text_lower for word in self.prohibited_words)

    def get_prohibited_words(self) -> List[str]:
        """
        Get the current list of prohibited words.

        Returns:
            List[str]: List of prohibited words.
        """
        return self.prohibited_words

    def add_prohibited_word(self, word: str):
        """
        Add a new prohibited word to the configuration.

        Args:
            word (str): Word to prohibit.
        """
        word_lower = word.lower()
        if word_lower not in self.prohibited_words:
            self.prohibited_words.append(word_lower)

    def remove_prohibited_word(self, word: str):
        """
        Remove a word from the prohibited words list.

        Args:
            word (str): Word to remove from prohibited words.
        """
        word_lower = word.lower()
        if word_lower in self.prohibited_words:
            self.prohibited_words.remove(word_lower)