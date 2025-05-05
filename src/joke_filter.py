from typing import List, Dict, Optional, Union

def filter_jokes(
    jokes: List[Dict[str, str]], 
    max_length: Optional[int] = None, 
    contains: Optional[str] = None, 
    exclude_contains: Optional[Union[str, List[str]]] = None,
    category: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Filter jokes based on various criteria.

    Args:
        jokes (List[Dict[str, str]]): List of joke dictionaries
        max_length (Optional[int]): Maximum joke length to include
        contains (Optional[str]): Substring that joke must contain
        exclude_contains (Optional[Union[str, List[str]]]): Substring(s) to exclude
        category (Optional[str]): Specific joke category to filter

    Returns:
        List[Dict[str, str]]: Filtered list of jokes
    """
    # Validate input types
    if not isinstance(jokes, list):
        raise TypeError("jokes must be a list of dictionaries")
    
    # Prepare exclude_contains as a list
    if exclude_contains is None:
        exclude_contains = []
    elif isinstance(exclude_contains, str):
        exclude_contains = [exclude_contains]

    # Filter the jokes
    filtered_jokes = []
    for joke in jokes:
        # Validate each joke is a dictionary with text
        if not isinstance(joke, dict) or 'text' not in joke:
            continue
        
        # Prepare text for comparison
        text = joke['text'].lower()
        
        # Check category if specified
        if category and joke.get('category') != category:
            continue
        
        # Check max length if specified
        if max_length and len(joke['text']) > max_length:
            continue
        
        # Check contains if specified
        if contains and contains.lower() not in text:
            continue
        
        # Check exclude_contains
        if any(ex.lower() in text for ex in exclude_contains):
            continue
        
        filtered_jokes.append(joke)
    
    return filtered_jokes