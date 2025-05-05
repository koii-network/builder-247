from typing import List, Optional, Union

def filter_jokes(
    jokes: List[str], 
    min_length: Optional[int] = None, 
    max_length: Optional[int] = None,
    contains: Optional[Union[str, List[str]]] = None,
    excludes: Optional[Union[str, List[str]]] = None
) -> List[str]:
    """
    Filter jokes based on various criteria.

    Args:
        jokes (List[str]): List of jokes to filter
        min_length (Optional[int]): Minimum length of joke
        max_length (Optional[int]): Maximum length of joke
        contains (Optional[Union[str, List[str]]]): Substring(s) to include
        excludes (Optional[Union[str, List[str]]]): Substring(s) to exclude

    Returns:
        List[str]: Filtered list of jokes
    """
    if not jokes:
        return []

    # Convert contains and excludes to lists if they are strings
    if isinstance(contains, str):
        contains = [contains]
    if isinstance(excludes, str):
        excludes = [excludes]

    filtered_jokes = jokes.copy()

    # Length filtering
    if min_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) >= min_length]
    
    if max_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) <= max_length]

    # Contains filtering
    if contains is not None:
        filtered_jokes = [
            joke for joke in filtered_jokes 
            if any(substr.lower() in joke.lower() for substr in contains)
        ]

    # Excludes filtering
    if excludes is not None:
        filtered_jokes = [
            joke for joke in filtered_jokes 
            if not any(substr.lower() in joke.lower() for substr in excludes)
        ]

    return filtered_jokes