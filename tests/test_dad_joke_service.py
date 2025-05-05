import pytest
from src.dad_joke_service import DadJokeService

def test_get_random_joke():
    """Test that get_random_joke returns a non-empty string."""
    service = DadJokeService()
    joke = service.get_random_joke()
    assert isinstance(joke, str)
    assert len(joke) > 0

def test_add_joke():
    """Test adding a new joke to the collection."""
    service = DadJokeService()
    initial_count = service.get_joke_count()
    new_joke = "Why did the math book look so sad? Because it had too many problems!"
    service.add_joke(new_joke)
    assert service.get_joke_count() == initial_count + 1
    assert new_joke in service.jokes

def test_add_duplicate_joke():
    """Test that adding a duplicate joke does not increase joke count."""
    service = DadJokeService()
    initial_count = service.get_joke_count()
    duplicate_joke = service.jokes[0]
    service.add_joke(duplicate_joke)
    assert service.get_joke_count() == initial_count

def test_add_joke_type_error():
    """Test that adding a non-string joke raises a TypeError."""
    service = DadJokeService()
    with pytest.raises(TypeError):
        service.add_joke(123)
    with pytest.raises(TypeError):
        service.add_joke(None)

def test_add_joke_value_error():
    """Test that adding an empty joke raises a ValueError."""
    service = DadJokeService()
    with pytest.raises(ValueError):
        service.add_joke("")
    with pytest.raises(ValueError):
        service.add_joke("   ")

def test_get_joke_count():
    """Test that get_joke_count returns the correct number of jokes."""
    service = DadJokeService()
    assert service.get_joke_count() > 0
    
    # Add a new joke and verify count
    initial_count = service.get_joke_count()
    service.add_joke("New test joke")
    assert service.get_joke_count() == initial_count + 1