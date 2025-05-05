import pytest
from src.joke_filter import filter_jokes

@pytest.fixture
def sample_jokes():
    return [
        "Why did the chicken cross the road?",
        "Why did the programmer quit his job?",
        "A short joke.",
        "This is a very long joke that goes on and on and contains lots of details about something funny.",
        "Why did the developer go broke? Because he used up all his cache!"
    ]

def test_no_filtering(sample_jokes):
    """Test that when no filters are applied, all jokes are returned."""
    result = filter_jokes(sample_jokes)
    assert len(result) == len(sample_jokes)

def test_min_length_filter(sample_jokes):
    """Test filtering jokes by minimum length."""
    result = filter_jokes(sample_jokes, min_length=40)
    assert len(result) == 1
    assert "very long joke" in result[0]

def test_max_length_filter(sample_jokes):
    """Test filtering jokes by maximum length."""
    result = filter_jokes(sample_jokes, max_length=25)
    assert len(result) == 2
    assert all(len(joke) <= 25 for joke in result)

def test_contains_filter(sample_jokes):
    """Test filtering jokes containing specific substrings."""
    result = filter_jokes(sample_jokes, contains="programmer")
    assert len(result) == 1
    assert "programmer" in result[0]

def test_contains_multiple_filter(sample_jokes):
    """Test filtering jokes containing multiple substrings."""
    result = filter_jokes(sample_jokes, contains=["programmer", "developer"])
    assert len(result) == 2

def test_excludes_filter(sample_jokes):
    """Test filtering out jokes with specific substrings."""
    result = filter_jokes(sample_jokes, excludes="road")
    assert len(result) == len(sample_jokes) - 1
    assert all("road" not in joke for joke in result)

def test_combines_filters(sample_jokes):
    """Test combining multiple filter criteria."""
    result = filter_jokes(
        sample_jokes, 
        min_length=10, 
        max_length=50, 
        contains="developer",
        excludes="broke"
    )
    assert len(result) == 0

def test_empty_input():
    """Test behavior with empty input list."""
    result = filter_jokes([])
    assert result == []

def test_case_insensitive_contains(sample_jokes):
    """Test that contains filter is case-insensitive."""
    result = filter_jokes(sample_jokes, contains="DEVELOPER")
    assert len(result) == 1
    assert "developer" in result[0].lower()

def test_case_insensitive_excludes(sample_jokes):
    """Test that excludes filter is case-insensitive."""
    result = filter_jokes(sample_jokes, excludes="ROAD")
    assert len(result) == len(sample_jokes) - 1
    assert all("road" not in joke.lower() for joke in result)