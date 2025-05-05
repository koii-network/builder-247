import pytest
from src.joke_filter import filter_jokes

def test_filter_jokes_by_keywords():
    jokes = [
        "I told my wife she was drawing her eyebrows too high.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Parallel lines have so much in common. It's a shame they'll never meet."
    ]
    
    # Filter jokes containing 'wife' or 'scarecrow'
    filtered = filter_jokes(jokes, keywords=['wife', 'scarecrow'])
    assert len(filtered) == 2
    assert "I told my wife she was drawing her eyebrows too high." in filtered
    assert "Why did the scarecrow win an award? Because he was outstanding in his field!" in filtered

def test_filter_jokes_by_min_length():
    jokes = ["Hi", "Short joke", "This is a longer joke about something funny"]
    
    # Filter jokes longer than 15 characters
    filtered = filter_jokes(jokes, min_length=15)
    assert len(filtered) == 1
    assert filtered[0] == "This is a longer joke about something funny"

def test_filter_jokes_by_max_length():
    jokes = ["Hi", "Short joke", "This is a longer joke about something funny"]
    
    # Filter jokes shorter than 15 characters
    filtered = filter_jokes(jokes, max_length=15)
    assert len(filtered) == 2
    assert "Hi" in filtered
    assert "Short joke" in filtered

def test_filter_jokes_multiple_criteria():
    jokes = [
        "Short joke",
        "Wife joke about something",
        "Long joke about a scarecrow in a field",
        "Another long joke that is very long"
    ]
    
    # Filter jokes containing 'wife' or 'scarecrow' and between 15-50 characters
    filtered = filter_jokes(jokes, keywords=['wife', 'scarecrow'], min_length=15, max_length=50)
    assert len(filtered) == 2
    assert "Wife joke about something" in filtered
    assert "Long joke about a scarecrow in a field" in filtered

def test_filter_jokes_no_match():
    jokes = ["Joke 1", "Joke 2", "Joke 3"]
    
    # Filter with keywords that don't exist
    filtered = filter_jokes(jokes, keywords=['unicorn'])
    assert len(filtered) == 0

def test_filter_jokes_none_input():
    # Test handling of None input
    filtered = filter_jokes(None)
    assert filtered == []

def test_filter_jokes_empty_list():
    # Test handling of empty list
    filtered = filter_jokes([])
    assert filtered == []

def test_filter_jokes_case_insensitive_keywords():
    jokes = ["UPPERCASE JOKE", "lowercase joke", "MiXeD cAsE joke"]
    
    filtered = filter_jokes(jokes, keywords=['joke'])
    assert len(filtered) == 3

def test_filter_jokes_empty_keywords():
    jokes = ["Joke 1", "Joke 2"]
    
    # Empty keywords should return all jokes
    filtered = filter_jokes(jokes, keywords=[])
    assert len(filtered) == 2