"""Test suite for error handling and logging utilities."""

import os
import json
import logging
import pytest
import tempfile
from unittest.mock import patch

from prometheus_swarm.utils.errors import (
    PrometheusBaseError,
    ConfigurationError,
    ClientAPIError,
    NetworkError,
    ResourceError,
    create_error
)

from prometheus_swarm.utils.logging import logger, log_execution_time


def test_base_error_creation():
    """Test creating base error with full context."""
    context = {"source": "test", "details": "Sample context"}
    error = PrometheusBaseError(
        "Test Error",
        error_code="TEST_CODE",
        context=context
    )

    assert str(error) == "[TEST_CODE] Test Error (Context: source: test | details: Sample context)"
    assert error.error_code == "TEST_CODE"
    assert error.context == context


def test_configuration_error():
    """Test ConfigurationError with specific context."""
    context = {"config_key": "missing_value"}
    error = ConfigurationError("Missing configuration", context=context)

    assert "CONFIG_ERROR" in str(error)
    assert "config_key: missing_value" in str(error)


def test_client_api_error():
    """Test ClientAPIError with status code."""
    original_error = ValueError("Internal server error")
    error = ClientAPIError(
        "API call failed",
        status_code=500,
        original_error=original_error
    )

    assert "API_ERROR_500" in str(error)
    assert "status_code: 500" in str(error)
    assert "original_error: Internal server error" in str(error)


def test_network_error():
    """Test NetworkError with host context."""
    error = NetworkError("Connection timeout", host="example.com")

    assert "NETWORK_ERROR" in str(error)
    assert "host: example.com" in str(error)


def test_resource_error():
    """Test ResourceError with resource type."""
    error = ResourceError("Insufficient memory", resource_type="RAM")

    assert "RESOURCE_ERROR" in str(error)
    assert "resource_type: RAM" in str(error)


def test_error_factory():
    """Test error factory method."""
    network_error = create_error("network", "Connection failed", host="localhost")
    config_error = create_error("config", "Invalid configuration", context={"key": "value"})

    assert isinstance(network_error, NetworkError)
    assert isinstance(config_error, ConfigurationError)
    assert "host: localhost" in str(network_error)


def test_execution_time_logging():
    """Test log_execution_time decorator."""
    @log_execution_time
    def sample_function(x, y):
        """Sample function for testing."""
        return x + y

    with patch.object(logger, 'info') as mock_log_info:
        result = sample_function(3, 4)
        assert result == 7
        mock_log_info.assert_called()
        log_call = mock_log_info.call_args[1]['extra']
        assert 'execution_time_ms' in log_call
        assert log_call['function'] == 'sample_function'


def test_structured_logging():
    """Test structured logging features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict(os.environ, {'PROMETHEUS_LOG_DIR': tmpdir}):
            test_logger = logger

            # Log various message types
            test_logger.debug("Debug message", extra={"context": "test"})
            test_logger.info("Info message", extra={"user_id": 123})
            test_logger.warning("Warning message", extra={"component": "tests"})
            
            try:
                1 / 0  # Raise an exception
            except ZeroDivisionError:
                test_logger.error("Division by zero", extra={"operation": "divide"})

            # Check log files
            log_files = [f for f in os.listdir(tmpdir) if f.endswith('.log')]
            assert len(log_files) > 0

            # Read the latest log file
            with open(os.path.join(tmpdir, log_files[-1]), 'r') as log_file:
                logs = log_file.readlines()
                assert any("Debug message" in log for log in logs)
                assert any("Info message" in log for log in logs)
                assert any("Warning message" in log for log in logs)
                assert any("Division by zero" in log for log in logs)