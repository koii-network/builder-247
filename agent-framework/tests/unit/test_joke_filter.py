"""
Unit tests for joke filtering functionality.
"""
import pytest
from prometheus_swarm.utils.joke_filter import filter_jokes

def test_filter_jokes_empty_input():
    """Test filtering an empty list of jokes."""
    assert filter_jokes([]) == []

def test_filter_jokes_no_filters():
    """Test that when no filters are applied, all jokes are returned."""
    jokes = ["Short joke", "Longer joke with more text", "Another joke"]
    assert filter_jokes(jokes) == jokes

def test_filter_jokes_min_length():
    """Test filtering jokes by minimum length."""
    jokes = ["Hi", "Hello", "This is a longer joke"]
    assert filter_jokes(jokes, min_length=10) == ["This is a longer joke"]

def test_filter_jokes_max_length():
    """Test filtering jokes by maximum length."""
    jokes = ["Hi", "Hello", "This is a longer joke"]
    assert filter_jokes(jokes, max_length=5) == ["Hi", "Hello"]

def test_filter_jokes_contains():
    """Test filtering jokes that contain a specific substring."""
    jokes = ["Cat joke", "Dog story", "Elephant tale"]
    assert filter_jokes(jokes, contains="cat") == ["Cat joke"]
    assert filter_jokes(jokes, contains="tale") == ["Elephant tale"]

def test_filter_jokes_contains_case_insensitive():
    """Test that contains filter is case-insensitive."""
    jokes = ["Cat Joke", "dog story", "ELEPHANT tale"]
    assert filter_jokes(jokes, contains="cat") == ["Cat Joke"]
    assert filter_jokes(jokes, contains="TALE") == ["ELEPHANT tale"]

def test_filter_jokes_exclude_contains():
    """Test filtering out jokes containing a specific substring."""
    jokes = ["Cat joke", "Dog story", "Elephant tale"]
    assert filter_jokes(jokes, exclude_contains="dog") == ["Cat joke", "Elephant tale"]

def test_filter_jokes_multiple_filters():
    """Test applying multiple filters simultaneously."""
    jokes = [
        "Short cat joke", 
        "Very long joke about an elephant", 
        "Medium dog story"
    ]
    result = filter_jokes(jokes, 
                           min_length=10, 
                           max_length=30, 
                           contains="dog")
    assert result == ["Medium dog story"]

def test_filter_jokes_no_match():
    """Test when no jokes match the filters."""
    jokes = ["Short joke", "Another short joke"]
    assert filter_jokes(jokes, contains="long", min_length=50) == []