import pytest
from prometheus_swarm.clients.base_client import Client
from prometheus_swarm.utils.errors import CustomError, ClientAPIError

class MockClient(Client):
    def __init__(self, raise_error=False):
        super().__init__()
        self.raise_error = raise_error

    def _get_default_model(self):
        return "test-model"

    def _get_api_name(self):
        return "MockAPI"

    def _convert_tool_to_api_format(self, tool):
        return {}

    def _convert_message_to_api_format(self, message):
        return {}

    def _convert_api_response_to_message(self, response):
        return {"content": [{"type": "text", "text": "Test response"}]}

    def _format_tool_response(self, response):
        return {"role": "tool", "content": []}

    def _make_api_call(self, **kwargs):
        if self.raise_error:
            raise ClientAPIError("API Error")
        return {"test": "response"}

    def _convert_tool_choice_to_api_format(self, tool_choice):
        return {}

def test_base_client_error_handling():
    """Test base client error handling mechanisms."""
    # Test successful initialization
    client = MockClient(raise_error=False)
    assert client is not None

    # Test API call error handling
    with pytest.raises(ClientAPIError, match="API Error"):
        MockClient(raise_error=True).send_message(prompt="Test")

def test_custom_error_attributes():
    """Verify CustomError attributes and behavior."""
    error_message = "Test custom error"
    custom_error = CustomError(error_message)

    assert str(custom_error) == error_message
    assert isinstance(custom_error, Exception)

def test_client_api_error():
    """Test ClientAPIError with additional context."""
    api_error = ClientAPIError(
        message="Test API error", 
        status_code=400, 
        response={"detail": "Bad request"}
    )

    assert str(api_error) == "Test API error"
    assert api_error.status_code == 400
    assert api_error.response == {"detail": "Bad request"}

def test_error_with_context():
    """Test creating CustomError with additional context."""
    context = {"module": "test_module", "operation": "test_op"}
    error_message = "Error with context"
    
    custom_error = CustomError(error_message, context=context)
    
    assert str(custom_error) == error_message
    assert custom_error.context == context

def test_error_context_manipulation():
    """Test adding and manipulating context in CustomError."""
    error = CustomError("Initial error")
    error.add_context("additional_info", "Extra details")

    assert error.context.get("additional_info") == "Extra details"