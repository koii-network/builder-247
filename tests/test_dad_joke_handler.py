"""
Unit tests for the Dad Joke Command Handler.
"""

import pytest
from src.dad_joke_handler import DadJokeCommandHandler


def test_initialization_with_default_jokes():
    """Test initialization with default jokes."""
    handler = DadJokeCommandHandler()
    assert handler.get_joke_count() > 0


def test_initialization_with_custom_jokes():
    """Test initialization with custom jokes."""
    custom_jokes = ["Joke 1", "Joke 2"]
    handler = DadJokeCommandHandler(initial_jokes=custom_jokes)
    assert handler.get_joke_count() == 2
    assert set(handler.list_jokes()) == set(custom_jokes)


def test_get_random_joke():
    """Test getting a random joke."""
    handler = DadJokeCommandHandler(initial_jokes=["Joke 1", "Joke 2"])
    joke = handler.get_random_joke()
    assert joke in ["Joke 1", "Joke 2"]


def test_get_random_joke_empty_collection():
    """Test getting a random joke from an empty collection."""
    handler = DadJokeCommandHandler(initial_jokes=[])
    with pytest.raises(ValueError, match="No jokes available"):
        handler.get_random_joke()


def test_add_joke():
    """Test adding a new joke."""
    handler = DadJokeCommandHandler()
    initial_count = handler.get_joke_count()
    
    # Add a new joke
    result = handler.add_joke("New funny joke")
    assert result is True
    assert handler.get_joke_count() == initial_count + 1
    assert "New funny joke" in handler.list_jokes()


def test_add_duplicate_joke():
    """Test adding a duplicate joke."""
    handler = DadJokeCommandHandler()
    initial_count = handler.get_joke_count()
    
    # Add a duplicate joke
    first_result = handler.add_joke("Duplicate joke")
    second_result = handler.add_joke("Duplicate joke")
    
    assert first_result is True
    assert second_result is False
    assert handler.get_joke_count() == initial_count + 1


def test_add_invalid_joke():
    """Test adding an invalid joke."""
    handler = DadJokeCommandHandler()
    with pytest.raises(ValueError, match="Joke must be a non-empty string"):
        handler.add_joke("")
    with pytest.raises(ValueError, match="Joke must be a non-empty string"):
        handler.add_joke(None)  # type: ignore


def test_remove_joke():
    """Test removing an existing joke."""
    initial_jokes = ["Joke 1", "Joke 2", "Joke 3"]
    handler = DadJokeCommandHandler(initial_jokes=initial_jokes)
    
    result = handler.remove_joke("Joke 2")
    assert result is True
    assert "Joke 2" not in handler.list_jokes()
    assert handler.get_joke_count() == 2


def test_remove_nonexistent_joke():
    """Test removing a nonexistent joke."""
    handler = DadJokeCommandHandler()
    result = handler.remove_joke("Nonexistent joke")
    assert result is False


def test_list_jokes():
    """Test listing jokes."""
    initial_jokes = ["Joke 1", "Joke 2"]
    handler = DadJokeCommandHandler(initial_jokes=initial_jokes)
    
    jokes = handler.list_jokes()
    assert set(jokes) == set(initial_jokes)
    
    # Ensure it's a copy, not the original list
    jokes.append("New joke")
    assert "New joke" not in handler.list_jokes()


def test_command_handler_random():
    """Test random joke command."""
    handler = DadJokeCommandHandler(initial_jokes=["Joke 1", "Joke 2"])
    
    result = handler.handle_command('random')
    assert result['success'] is True
    assert 'joke' in result
    assert result['joke'] in ["Joke 1", "Joke 2"]


def test_command_handler_add():
    """Test add joke command."""
    handler = DadJokeCommandHandler()
    initial_count = handler.get_joke_count()
    
    result = handler.handle_command('add', joke="New funny joke")
    assert result['success'] is True
    assert result['joke'] == "New funny joke"
    assert handler.get_joke_count() == initial_count + 1


def test_command_handler_add_invalid():
    """Test add joke command with invalid input."""
    handler = DadJokeCommandHandler()
    
    with pytest.raises(ValueError, match="Joke is required"):
        handler.handle_command('add')


def test_command_handler_remove():
    """Test remove joke command."""
    initial_jokes = ["Joke 1", "Joke 2"]
    handler = DadJokeCommandHandler(initial_jokes=initial_jokes)
    
    result = handler.handle_command('remove', joke="Joke 1")
    assert result['success'] is True
    assert result['joke'] == "Joke 1"
    assert "Joke 1" not in handler.list_jokes()


def test_command_handler_remove_invalid():
    """Test remove joke command with invalid input."""
    handler = DadJokeCommandHandler()
    
    with pytest.raises(ValueError, match="Joke is required"):
        handler.handle_command('remove')


def test_command_handler_list():
    """Test list jokes command."""
    initial_jokes = ["Joke 1", "Joke 2"]
    handler = DadJokeCommandHandler(initial_jokes=initial_jokes)
    
    result = handler.handle_command('list')
    assert result['success'] is True
    assert set(result['jokes']) == set(initial_jokes)
    assert result['count'] == 2


def test_command_handler_invalid_command():
    """Test invalid command handling."""
    handler = DadJokeCommandHandler()
    
    with pytest.raises(ValueError, match="Unknown command"):
        handler.handle_command('invalid_command')