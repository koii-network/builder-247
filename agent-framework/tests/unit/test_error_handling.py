import pytest
from prometheus_swarm.utils.errors import CustomError
from prometheus_swarm.clients.base_client import BaseClient

class MockClient(BaseClient):
    def __init__(self, raise_error=False):
        super().__init__()
        self.raise_error = raise_error

    def _validate_configuration(self):
        if self.raise_error:
            raise CustomError("Configuration validation failed")

def test_base_client_error_handling():
    """Test base client error handling mechanisms."""
    # Test successful initialization
    client = MockClient(raise_error=False)
    assert client is not None

    # Test error raised during configuration validation
    with pytest.raises(CustomError, match="Configuration validation failed"):
        MockClient(raise_error=True)

def test_custom_error_attributes():
    """Verify CustomError attributes and behavior."""
    error_message = "Test custom error"
    custom_error = CustomError(error_message)

    assert str(custom_error) == error_message
    assert isinstance(custom_error, Exception)

def test_error_with_context():
    """Test creating CustomError with additional context."""
    context = {"module": "test_module", "operation": "test_op"}
    error_message = "Error with context"
    
    custom_error = CustomError(error_message, context=context)
    
    assert str(custom_error) == error_message
    assert custom_error.context == context

def test_error_inheritance():
    """Ensure CustomError can be caught by generic Exception handlers."""
    try:
        raise CustomError("Test inheritance")
    except Exception as e:
        assert isinstance(e, CustomError)
        assert isinstance(e, Exception)

def test_multiple_error_instantiation():
    """Test creating multiple CustomError instances."""
    error1 = CustomError("First error")
    error2 = CustomError("Second error")

    assert str(error1) != str(error2)
    assert error1 is not error2

def test_error_with_no_message():
    """Test creating a CustomError without a message."""
    error = CustomError()
    assert str(error) == ""

def test_context_manipulation():
    """Test adding and manipulating context in CustomError."""
    error = CustomError("Initial error")
    error.context["additional_info"] = "Extra details"

    assert error.context.get("additional_info") == "Extra details"