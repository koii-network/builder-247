import pytest
from src.joke_filter import JokeFilter

@pytest.fixture
def sample_jokes():
    return [
        {'text': 'Short joke', 'category': 'clean', 'words': 3},
        {'text': 'Longer joke about something funny', 'category': 'general', 'words': 7},
        {'text': 'Very long joke with many words that goes on and on', 'category': 'long', 'words': 12},
        {'text': 'Explicit adult content joke', 'category': 'NSFW', 'words': 6},
        {'text': 'Another short joke', 'category': 'clean', 'words': 4}
    ]

def test_filter_jokes_with_no_filters(sample_jokes):
    result = JokeFilter.filter_jokes(sample_jokes)
    assert len(result) == len(sample_jokes)

def test_filter_jokes_by_category(sample_jokes):
    clean_filter = JokeFilter.by_category('clean')
    result = JokeFilter.filter_jokes(sample_jokes, [clean_filter])
    
    assert len(result) == 2
    assert all(joke['category'] == 'clean' for joke in result)

def test_filter_jokes_by_complexity(sample_jokes):
    complexity_filter = JokeFilter.by_complexity(5)
    result = JokeFilter.filter_jokes(sample_jokes, [complexity_filter])
    
    assert len(result) == 3
    assert all(len(joke['text'].split()) <= 5 for joke in result)

def test_exclude_explicit_content(sample_jokes):
    explicit_filter = JokeFilter.exclude_explicit_content()
    result = JokeFilter.filter_jokes(sample_jokes, [explicit_filter])
    
    assert len(result) == 4
    assert all('nsfw' not in joke['category'].lower() for joke in result)

def test_multiple_filters(sample_jokes):
    category_filter = JokeFilter.by_category('clean')
    complexity_filter = JokeFilter.by_complexity(5)
    
    result = JokeFilter.filter_jokes(sample_jokes, [category_filter, complexity_filter])
    
    assert len(result) == 1
    assert result[0]['category'] == 'clean'
    assert len(result[0]['text'].split()) <= 5

def test_invalid_input_types():
    with pytest.raises(TypeError, match="Jokes must be a list"):
        JokeFilter.filter_jokes("not a list")
    
    with pytest.raises(TypeError, match="All filters must be callable functions"):
        JokeFilter.filter_jokes([], [1, 2, 3])

def test_empty_jokes_list():
    assert JokeFilter.filter_jokes([]) == []
    assert JokeFilter.filter_jokes([], []) == []