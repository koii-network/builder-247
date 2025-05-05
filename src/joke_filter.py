def filter_jokes(jokes, keywords=None, min_length=None, max_length=None):
    """
    Filter jokes based on optional criteria.

    Args:
        jokes (list): A list of joke strings to filter.
        keywords (list, optional): Jokes must contain at least one of these keywords.
        min_length (int, optional): Minimum joke length (inclusive).
        max_length (int, optional): Maximum joke length (inclusive).

    Returns:
        list: Filtered list of jokes matching the specified criteria.
    """
    if jokes is None:
        return []

    filtered_jokes = jokes.copy()

    # Filter by keywords if specified
    if keywords:
        filtered_jokes = [joke for joke in filtered_jokes 
                          if any(keyword.lower() in joke.lower() for keyword in keywords)]

    # Filter by minimum length if specified
    if min_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) >= min_length]

    # Filter by maximum length if specified
    if max_length is not None:
        filtered_jokes = [joke for joke in filtered_jokes if len(joke) <= max_length]

    return filtered_jokes