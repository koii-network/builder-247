"""
Unit tests for Dad Joke Command Handler.
"""

import pytest
from prometheus_swarm.tools.dad_joke_handler import DadJokeCommandHandler


class MockDadJokeHandler(DadJokeCommandHandler):
    """
    Mock implementation of Dad Joke Command Handler for testing.
    """

    def __init__(self):
        self._jokes = {
            'default': [
                'Why don\'t scientists trust atoms? Because they make up everything!',
                'I told my wife she was drawing her eyebrows too high. She looked surprised.'
            ],
            'science': [
                'Why do scientists trust atoms? Because they make up everything!',
                'I have a joke about chemistry, but I don\'t think it will get a reaction.'
            ]
        }

    def get_random_joke(self) -> str:
        all_jokes = [joke for category in self._jokes.values() for joke in category]
        if not all_jokes:
            raise RuntimeError("No jokes available")
        return random.choice(all_jokes)

    def get_joke_by_category(self, category: str) -> str:
        if category not in self._jokes:
            raise ValueError(f"Invalid category: {category}")
        category_jokes = self._jokes[category]
        if not category_jokes:
            raise RuntimeError(f"No jokes available in category: {category}")
        return random.choice(category_jokes)

    def add_joke(self, joke: str, category: str = 'default') -> bool:
        if not joke or len(joke.strip()) == 0:
            raise ValueError("Joke cannot be empty")
        
        category = category or 'default'
        if category not in self._jokes:
            self._jokes[category] = []
        
        if joke in self._jokes[category]:
            return False
        
        self._jokes[category].append(joke)
        return True

    def get_joke_categories(self) -> list:
        return list(self._jokes.keys())


def test_dad_joke_interface():
    """
    Test the core functionality of the Dad Joke Command Handler.
    """
    handler = MockDadJokeHandler()

    # Test getting random joke
    random_joke = handler.get_random_joke()
    assert isinstance(random_joke, str)
    assert len(random_joke) > 0

    # Test getting joke by category
    science_joke = handler.get_joke_by_category('science')
    assert isinstance(science_joke, str)
    assert science_joke in handler.get_joke_categories()

    # Test adding a joke
    new_joke = 'I used to be a baker, but I didn\'t make enough dough.'
    assert handler.add_joke(new_joke, 'career') == True
    assert 'career' in handler.get_joke_categories()

    # Test adding duplicate joke
    assert handler.add_joke(new_joke, 'career') == False


def test_error_handling():
    """
    Test error scenarios in the Dad Joke Command Handler.
    """
    handler = MockDadJokeHandler()

    # Test invalid category
    with pytest.raises(ValueError):
        handler.get_joke_by_category('nonexistent')

    # Test empty joke
    with pytest.raises(ValueError):
        handler.add_joke('')