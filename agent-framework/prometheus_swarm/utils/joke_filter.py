"""
Joke filtering utility functions for managing and filtering jokes.
"""

def filter_joke(joke: str, max_length: int = 250, blacklist_words: list = None) -> bool:
    """
    Filter a joke based on length and optional blacklist words.
    
    Args:
        joke (str): The joke text to filter
        max_length (int, optional): Maximum allowed length for the joke. Defaults to 250.
        blacklist_words (list, optional): List of words that would disqualify the joke. Defaults to None.
    
    Returns:
        bool: True if the joke passes all filters, False otherwise
    """
    if not isinstance(joke, str):
        return False
    
    # Check joke length
    if len(joke) > max_length:
        return False
    
    # Check for blacklist words if provided
    if blacklist_words:
        joke_lower = joke.lower()
        if any(word.lower() in joke_lower for word in blacklist_words):
            return False
    
    return True

def clean_joke(joke: str) -> str:
    """
    Clean a joke by removing leading/trailing whitespaces and standardizing format.
    
    Args:
        joke (str): The joke text to clean
    
    Returns:
        str: Cleaned joke text
    """
    if not isinstance(joke, str):
        return ""
    
    return joke.strip()