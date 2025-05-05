"""Utility modules for Prometheus Swarm."""

from .error_handling import (
    BasePrometheusError,
    ConfigurationError,
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError,
    handle_and_log_errors,
    retry_on_error
)

from .logging import (
    logger,
    log_error,
    log_section,
    log_key_value,
    log_tool_call,
    log_tool_result,
    log_execution_time,
    add_file_logging
)

__all__ = [
    # Error Handling
    'BasePrometheusError',
    'ConfigurationError',
    'AuthenticationError',
    'ResourceNotFoundError',
    'NetworkError',
    'handle_and_log_errors',
    'retry_on_error',
    
    # Logging
    'logger',
    'log_error',
    'log_section',
    'log_key_value',
    'log_tool_call',
    'log_tool_result',
    'log_execution_time',
    'add_file_logging'
]