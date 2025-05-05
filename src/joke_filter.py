def filter_jokes(jokes, filter_criteria=None):
    """
    Filter jokes based on given criteria.

    Args:
        jokes (list): A list of jokes to filter.
        filter_criteria (dict, optional): A dictionary of filtering rules. 
            Supports filtering by:
            - 'min_length': Minimum joke length
            - 'max_length': Maximum joke length
            - 'contains': Must contain specific word/phrase
            - 'excludes': Must not contain specific word/phrase
            - 'categories': List of allowed joke categories

    Returns:
        list: Filtered list of jokes that meet the specified criteria.

    Raises:
        ValueError: If filter_criteria is not a dictionary or if joke is invalid.
    """
    # If no filter criteria provided, return all jokes
    if filter_criteria is None:
        return jokes

    # Validate filter_criteria is a dictionary
    if not isinstance(filter_criteria, dict):
        raise ValueError("Filter criteria must be a dictionary")

    # Validate jokes input
    if not all(isinstance(joke, dict) for joke in jokes):
        raise ValueError("Each joke must be a dictionary")

    filtered_jokes = []
    for joke in jokes:
        # Default to empty strings if keys are missing
        joke_text = joke.get('text', '')
        joke_category = joke.get('category', '')

        # Length filtering
        min_length = filter_criteria.get('min_length')
        max_length = filter_criteria.get('max_length')
        
        if min_length is not None and len(joke_text) < min_length:
            continue
        
        if max_length is not None and len(joke_text) > max_length:
            continue

        # Contains filtering
        contains = filter_criteria.get('contains')
        if contains and contains.lower() not in joke_text.lower():
            continue

        # Excludes filtering
        excludes = filter_criteria.get('excludes')
        if excludes and excludes.lower() in joke_text.lower():
            continue

        # Categories filtering
        categories = filter_criteria.get('categories')
        if categories and joke_category.lower() not in [cat.lower() for cat in categories]:
            continue

        # If joke passes all filters, add to results
        filtered_jokes.append(joke)

    return filtered_jokes