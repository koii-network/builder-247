"""
Module for joke filtering logic.

This module provides functionality to filter jokes based on various criteria.
"""

def filter_jokes(jokes, max_length=None, exclude_keywords=None, min_rating=None):
    """
    Filter jokes based on multiple optional criteria.

    Args:
        jokes (list): A list of joke dictionaries to filter.
        max_length (int, optional): Maximum allowed length of a joke. 
        exclude_keywords (list, optional): Keywords to exclude jokes containing.
        min_rating (float, optional): Minimum rating for jokes.

    Returns:
        list: Filtered list of jokes meeting the specified criteria.
    """
    if jokes is None:
        return []

    filtered_jokes = jokes.copy()

    # Filter by max length if specified
    if max_length is not None:
        filtered_jokes = [
            joke for joke in filtered_jokes 
            if len(joke.get('text', '')) <= max_length
        ]

    # Filter by exclude keywords if specified
    if exclude_keywords is not None:
        filtered_jokes = [
            joke for joke in filtered_jokes
            if not any(
                keyword.lower() in joke.get('text', '').lower() 
                for keyword in exclude_keywords
            )
        ]

    # Filter by minimum rating if specified
    if min_rating is not None:
        filtered_jokes = [
            joke for joke in filtered_jokes
            if joke.get('rating', 0) >= min_rating
        ]

    return filtered_jokes