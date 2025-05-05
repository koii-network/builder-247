import pytest
from src.joke_filter import filter_jokes

def test_no_filter():
    """Test that when no filter is provided, all jokes are returned."""
    jokes = [
        {'text': 'Joke 1', 'category': 'Pun'},
        {'text': 'Joke 2', 'category': 'Knock Knock'}
    ]
    assert len(filter_jokes(jokes)) == 2

def test_min_length_filter():
    """Test filtering jokes by minimum length."""
    jokes = [
        {'text': 'Short', 'category': 'Pun'},
        {'text': 'This is a longer joke', 'category': 'Dad'}
    ]
    filtered = filter_jokes(jokes, {'min_length': 10})
    assert len(filtered) == 1
    assert filtered[0]['text'] == 'This is a longer joke'

def test_max_length_filter():
    """Test filtering jokes by maximum length."""
    jokes = [
        {'text': 'Short', 'category': 'Pun'},
        {'text': 'This is a very long joke that goes on and on', 'category': 'Dad'}
    ]
    filtered = filter_jokes(jokes, {'max_length': 10})
    assert len(filtered) == 1
    assert filtered[0]['text'] == 'Short'

def test_contains_filter():
    """Test filtering jokes that contain a specific word."""
    jokes = [
        {'text': 'A chicken joke', 'category': 'Animal'},
        {'text': 'A bear walks into a bar', 'category': 'Animal'}
    ]
    filtered = filter_jokes(jokes, {'contains': 'chicken'})
    assert len(filtered) == 1
    assert filtered[0]['text'] == 'A chicken joke'

def test_excludes_filter():
    """Test filtering jokes that do not contain a specific word."""
    jokes = [
        {'text': 'A chicken joke', 'category': 'Animal'},
        {'text': 'A bear walks into a bar', 'category': 'Animal'}
    ]
    filtered = filter_jokes(jokes, {'excludes': 'chicken'})
    assert len(filtered) == 1
    assert filtered[0]['text'] == 'A bear walks into a bar'

def test_categories_filter():
    """Test filtering jokes by allowed categories."""
    jokes = [
        {'text': 'Pun joke', 'category': 'Pun'},
        {'text': 'Dad joke', 'category': 'Dad'},
        {'text': 'Knock knock joke', 'category': 'Knock Knock'}
    ]
    filtered = filter_jokes(jokes, {'categories': ['Pun', 'Dad']})
    assert len(filtered) == 2
    assert {joke['category'] for joke in filtered} == {'Pun', 'Dad'}

def test_combined_filters():
    """Test strict combined filtering criteria."""
    jokes = [
        {'text': 'Short chicken joke', 'category': 'Animal'},
        {'text': 'A very long joke about a chicken', 'category': 'Animal'},
        {'text': 'No chicken here', 'category': 'Dad'}
    ]
    filtered = filter_jokes(jokes, {
        'min_length': 20,  # Explicitly set to filter longer jokes
        'contains': 'chicken',
        'categories': ['Animal']
    })
    assert len(filtered) == 1
    assert filtered[0]['text'] == 'A very long joke about a chicken'

def test_invalid_filter_criteria():
    """Test that an invalid filter criteria raises a ValueError."""
    jokes = [{'text': 'Joke', 'category': 'Pun'}]
    
    with pytest.raises(ValueError, match="Filter criteria must be a dictionary"):
        filter_jokes(jokes, "not a dictionary")

def test_invalid_joke_structure():
    """Test that an invalid joke structure without 'text' key raises a ValueError."""
    jokes = [{'category': 'Pun'}]
    
    with pytest.raises(ValueError, match="Each joke must be a dictionary with a 'text' key"):
        filter_jokes(jokes)