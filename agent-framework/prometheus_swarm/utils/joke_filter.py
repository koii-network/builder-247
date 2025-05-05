"""
Module for filtering jokes based on various criteria.
"""
from typing import List, Optional

def filter_jokes(jokes: List[str], 
                 min_length: Optional[int] = None, 
                 max_length: Optional[int] = None, 
                 contains: Optional[str] = None,
                 exclude_contains: Optional[str] = None) -> List[str]:
    """
    Filter jokes based on multiple criteria.

    Args:
        jokes (List[str]): List of jokes to filter
        min_length (Optional[int]): Minimum length of joke text. Defaults to None.
        max_length (Optional[int]): Maximum length of joke text. Defaults to None.
        contains (Optional[str]): Substring that joke must contain. Defaults to None.
        exclude_contains (Optional[str]): Substring that joke must not contain. Defaults to None.

    Returns:
        List[str]: Filtered list of jokes
    """
    if not jokes:
        return []

    filtered_jokes = jokes.copy()

    # Apply minimum length filter
    if min_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) >= min_length]

    # Apply maximum length filter
    if max_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) <= max_length]

    # Apply contains filter
    if contains is not None:
        filtered_jokes = [joke for joke in filtered_jokes if contains.lower() in joke.lower()]

    # Apply exclude contains filter
    if exclude_contains is not None:
        filtered_jokes = [joke for joke in filtered_jokes if exclude_contains.lower() not in joke.lower()]

    return filtered_jokes