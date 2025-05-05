import pytest
from src.joke_filter import filter_jokes

@pytest.fixture
def sample_jokes():
    return [
        {'text': 'A funny joke about dogs', 'category': 'animals'},
        {'text': 'A hilarious joke about cats', 'category': 'animals'},
        {'text': 'A long joke that goes on and on about nothing in particular', 'category': 'random'},
        {'text': 'Short joke', 'category': 'misc'}
    ]

def test_filter_jokes_no_filters(sample_jokes):
    result = filter_jokes(sample_jokes)
    assert len(result) == len(sample_jokes)

def test_filter_by_max_length(sample_jokes):
    result = filter_jokes(sample_jokes, max_length=10)
    assert len(result) == 1
    assert result[0]['text'] == 'Short joke'

def test_filter_by_contains(sample_jokes):
    result = filter_jokes(sample_jokes, contains='dogs')
    assert len(result) == 1
    assert 'dogs' in result[0]['text']

def test_filter_by_category(sample_jokes):
    result = filter_jokes(sample_jokes, category='animals')
    assert len(result) == 2
    assert all(joke['category'] == 'animals' for joke in result)

def test_filter_exclude_contains(sample_jokes):
    result = filter_jokes(sample_jokes, exclude_contains='long')
    assert len(result) == 3
    assert all('long' not in joke['text'] for joke in result)

def test_filter_multiple_exclude_contains(sample_jokes):
    result = filter_jokes(sample_jokes, exclude_contains=['long', 'dogs'])
    assert len(result) == 2
    assert all('long' not in joke['text'] and 'dogs' not in joke['text'] for joke in result)

def test_invalid_input_type():
    with pytest.raises(TypeError):
        filter_jokes("not a list")

def test_invalid_joke_type(sample_jokes):
    invalid_jokes = sample_jokes + [123]  # Add an invalid item
    result = filter_jokes(invalid_jokes)
    assert len(result) == len(sample_jokes)

def test_multiple_filters(sample_jokes):
    result = filter_jokes(
        sample_jokes, 
        max_length=20, 
        contains='joke', 
        category='animals'
    )
    assert len(result) == 1
    assert result[0]['text'] == 'A funny joke about dogs'