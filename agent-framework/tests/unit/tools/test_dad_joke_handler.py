import pytest
from typing import Protocol
from prometheus_swarm.tools.dad_joke_handler import DadJokeCommandHandlerProtocol

def test_dad_joke_command_handler_protocol():
    """
    Test that the DadJokeCommandHandlerProtocol has the required methods
    and follows the expected type signatures.
    """
    # Verify Protocol has correct methods
    assert hasattr(DadJokeCommandHandlerProtocol, 'get_random_joke'), "Missing get_random_joke method"
    assert hasattr(DadJokeCommandHandlerProtocol, 'get_joke_by_category'), "Missing get_joke_by_category method"
    assert hasattr(DadJokeCommandHandlerProtocol, 'rate_joke'), "Missing rate_joke method"

class MockDadJokeHandler:
    """A mock implementation to verify Protocol compliance"""
    def get_random_joke(self) -> str:
        return "Why don't scientists trust atoms? Because they make up everything!"
    
    def get_joke_by_category(self, category: str) -> str:
        if category not in ['science', 'dad', 'pun']:
            raise ValueError("Invalid category")
        return "I told my wife she was drawing her eyebrows too high. She looked surprised."
    
    def rate_joke(self, joke: str, rating: int) -> bool:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return True

def test_mock_handler_compliance():
    """
    Verify that a mock implementation meets the Protocol requirements
    """
    handler = MockDadJokeHandler()
    
    # Test random joke retrieval
    joke = handler.get_random_joke()
    assert isinstance(joke, str)
    assert len(joke) > 0
    
    # Test joke by category
    joke = handler.get_joke_by_category('science')
    assert isinstance(joke, str)
    assert len(joke) > 0
    
    with pytest.raises(ValueError):
        handler.get_joke_by_category('invalid_category')
    
    # Test joke rating
    assert handler.rate_joke("A funny joke", 3) is True
    
    with pytest.raises(ValueError):
        handler.rate_joke("A joke", 0)
    with pytest.raises(ValueError):
        handler.rate_joke("A joke", 6)

def test_protocol_runtime_checkable():
    """
    Verify that the Protocol can be runtime checked
    """
    assert isinstance(MockDadJokeHandler(), DadJokeCommandHandlerProtocol)