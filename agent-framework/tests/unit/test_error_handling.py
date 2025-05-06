import pytest
from prometheus_swarm.utils import errors

def test_custom_error_types():
    """Test custom error types defined in the application."""
    # Test ConfigurationError
    with pytest.raises(errors.ConfigurationError):
        raise errors.ConfigurationError("Test configuration error")
    
    # Test AuthenticationError
    with pytest.raises(errors.AuthenticationError):
        raise errors.AuthenticationError("Test authentication error")
    
    # Test ResourceNotFoundError
    with pytest.raises(errors.ResourceNotFoundError):
        raise errors.ResourceNotFoundError("Test resource not found")

def test_error_details():
    """Verify error messages are correctly captured."""
    error_msg = "Specific error details"
    
    config_error = errors.ConfigurationError(error_msg)
    assert str(config_error) == error_msg
    
    auth_error = errors.AuthenticationError(error_msg)
    assert str(auth_error) == error_msg
    
    resource_error = errors.ResourceNotFoundError(error_msg)
    assert str(resource_error) == error_msg

def test_error_inheritance():
    """Test that custom errors inherit from base exception."""
    assert issubclass(errors.ConfigurationError, Exception)
    assert issubclass(errors.AuthenticationError, Exception)
    assert issubclass(errors.ResourceNotFoundError, Exception)

def test_multiple_error_scenarios():
    """Test multiple error scenarios with context."""
    def simulate_nested_errors():
        try:
            try:
                raise ValueError("Initial low-level error")
            except ValueError as e:
                raise errors.ConfigurationError("Wrapper configuration error") from e
        except errors.ConfigurationError as config_error:
            return config_error
    
    config_error = simulate_nested_errors()
    assert isinstance(config_error, errors.ConfigurationError)
    assert "Initial low-level error" in str(config_error.__cause__)

def test_error_context_preservation():
    """Ensure error context is preserved when raising custom errors."""
    def error_chain_function():
        try:
            raise RuntimeError("Original runtime error")
        except RuntimeError as original_error:
            raise errors.ResourceNotFoundError("Resource lookup failed") from original_error
    
    with pytest.raises(errors.ResourceNotFoundError) as excinfo:
        error_chain_function()
    
    # Verify original error is preserved
    assert isinstance(excinfo.value.__cause__, RuntimeError)
    assert str(excinfo.value.__cause__) == "Original runtime error"

def test_error_attributes():
    """Test that errors can carry additional context."""
    error_context = {
        "resource_id": "abc123",
        "action": "retrieve"
    }
    
    config_error = errors.ConfigurationError(
        "Configuration failed", 
        context=error_context
    )
    
    assert config_error.context == error_context