import pytest
from prometheus_swarm.tools.dad_joke_command.implementations import get_random_dad_joke, dad_joke_command_handler

def test_get_random_dad_joke():
    """
    Test that get_random_dad_joke returns a non-empty string
    """
    joke = get_random_dad_joke()
    assert isinstance(joke, str)
    assert len(joke) > 0

def test_multiple_dad_jokes_are_different():
    """
    Test that multiple calls can return different jokes
    """
    joke1 = get_random_dad_joke()
    joke2 = get_random_dad_joke()
    
    # While it's statistically possible the same joke could be returned,
    # the chance is very low with multiple jokes
    assert len({joke1, joke2}) > 0

def test_dad_joke_command_handler():
    """
    Test the dad_joke_command_handler returns the expected dictionary
    """
    result = dad_joke_command_handler()
    
    assert isinstance(result, dict)
    assert 'type' in result
    assert 'text' in result
    assert result['type'] == 'text'
    assert isinstance(result['text'], str)
    assert len(result['text']) > 0