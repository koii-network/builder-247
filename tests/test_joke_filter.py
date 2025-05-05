"""
Test suite for joke filtering logic.
"""

import pytest
from src.joke_filter import filter_jokes

@pytest.fixture
def sample_jokes():
    """Fixture providing a sample list of jokes for testing."""
    return [
        {
            'text': 'Why did the chicken cross the road?',
            'rating': 3.5,
            'category': 'classic'
        },
        {
            'text': 'A programmer\'s wife tells him: Go to the store and buy bread. If they have eggs, bring a dozen.',
            'rating': 4.2,
            'category': 'programming'
        },
        {
            'text': 'Short joke.',
            'rating': 2.1,
            'category': 'misc'
        },
        {
            'text': 'A very long joke that contains multiple sentences and goes on and on about something funny and intricate.',
            'rating': 3.8,
            'category': 'long'
        }
    ]

def test_filter_jokes_no_criteria(sample_jokes):
    """Test filtering with no criteria applied."""
    result = filter_jokes(sample_jokes)
    assert len(result) == len(sample_jokes)

def test_filter_jokes_max_length(sample_jokes):
    """Test filtering jokes by maximum length."""
    result = filter_jokes(sample_jokes, max_length=40)
    assert len(result) == 2
    assert all(len(joke['text']) <= 40 for joke in result)

def test_filter_jokes_exclude_keywords(sample_jokes):
    """Test filtering jokes by excluded keywords."""
    result = filter_jokes(sample_jokes, exclude_keywords=['programmer'])
    assert len(result) == 3
    assert not any('programmer' in joke['text'].lower() for joke in result)

def test_filter_jokes_min_rating(sample_jokes):
    """Test filtering jokes by minimum rating."""
    result = filter_jokes(sample_jokes, min_rating=3.6)
    assert len(result) == 2
    assert all(joke['rating'] >= 3.6 for joke in result)

def test_filter_jokes_multiple_criteria(sample_jokes):
    """Test filtering jokes with multiple criteria."""
    result = filter_jokes(
        sample_jokes, 
        max_length=50, 
        exclude_keywords=['very'], 
        min_rating=3.0
    )
    assert len(result) == 2
    assert all(
        len(joke['text']) <= 50 and 
        'very' not in joke['text'].lower() and 
        joke['rating'] >= 3.0 
        for joke in result
    )

def test_filter_jokes_none_input():
    """Test behavior when input is None."""
    result = filter_jokes(None)
    assert result == []

def test_filter_jokes_empty_list():
    """Test behavior with an empty list of jokes."""
    result = filter_jokes([])
    assert result == []