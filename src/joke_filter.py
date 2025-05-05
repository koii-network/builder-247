from typing import List, Dict, Optional, Callable

class JokeFilter:
    """
    A flexible joke filtering mechanism that allows multiple filtering strategies.
    """
    
    @staticmethod
    def filter_jokes(
        jokes: List[Dict[str, str]], 
        filters: Optional[List[Callable[[Dict[str, str]], bool]]] = None
    ) -> List[Dict[str, str]]:
        """
        Filter jokes based on provided filter functions.
        
        Args:
            jokes (List[Dict[str, str]]): List of joke dictionaries to filter
            filters (Optional[List[Callable]]): List of filter functions to apply
        
        Returns:
            List[Dict[str, str]]: Filtered list of jokes
        
        Raises:
            TypeError: If jokes is not a list or filter is not a callable
        """
        if not isinstance(jokes, list):
            raise TypeError("Jokes must be a list")
        
        if filters is None:
            return jokes
        
        if not all(callable(f) for f in filters):
            raise TypeError("All filters must be callable functions")
        
        return [
            joke for joke in jokes 
            if all(filter_func(joke) for filter_func in filters)
        ]
    
    @staticmethod
    def by_category(category: str) -> Callable[[Dict[str, str]], bool]:
        """
        Create a filter function to filter jokes by category.
        
        Args:
            category (str): Category to filter by
        
        Returns:
            Callable: A filter function that checks joke category
        """
        return lambda joke: joke.get('category', '').lower() == category.lower()
    
    @staticmethod
    def by_complexity(max_words: int) -> Callable[[Dict[str, str]], bool]:
        """
        Create a filter function to filter jokes by maximum word count.
        
        Args:
            max_words (int): Maximum number of words allowed in a joke
        
        Returns:
            Callable: A filter function that checks joke word count
        """
        return lambda joke: len(joke.get('text', '').split()) <= max_words
    
    @staticmethod
    def exclude_explicit_content() -> Callable[[Dict[str, str]], bool]:
        """
        Create a filter function to exclude explicit jokes.
        
        Returns:
            Callable: A filter function that checks for explicit content
        """
        explicit_keywords = ['adult', 'nsfw', 'explicit']
        return lambda joke: not any(
            keyword in joke.get('category', '').lower() for keyword in explicit_keywords
        )