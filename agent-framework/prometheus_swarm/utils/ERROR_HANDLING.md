# Comprehensive Error Handling Utilities

## Overview
This module provides robust error handling and logging utilities for the Prometheus framework, designed to offer detailed, consistent, and contextual error information.

## Key Components

### Base Error Classes
- `PrometheusBaseError`: A foundational error class with comprehensive error tracking
- `ClientAPIError`: Specialized error for API-related issues
- `ConfigurationError`: Error class for configuration and environment setup issues

### Features
- Detailed error context
- Consistent error formatting
- Optional error logging
- Stacktrace preservation
- Flexible error handling decorators

## Usage Examples

### Basic Error Raising
```python
from prometheus_swarm.utils.errors import PrometheusBaseError

raise PrometheusBaseError(
    message="Something went wrong",
    error_code="EXAMPLE_ERROR",
    context={"input": "invalid_data"}
)
```

### Error Handling Decorator
```python
from prometheus_swarm.utils.errors import handle_and_log_error

@handle_and_log_error(
    logger_func=custom_logger,
    error_type=ClientAPIError,
    context={"endpoint": "/api/example"}
)
def api_call():
    # Function implementation
    pass
```

### Safe Execution
```python
from prometheus_swarm.utils.errors import safe_execute

result = safe_execute(
    risky_function,
    default_return=None,
    error_handler=log_error
)
```

## Best Practices
1. Always provide meaningful error codes
2. Include comprehensive context
3. Use decorators for consistent error handling
4. Leverage safe execution for critical operations

## Error Logging
Errors are automatically logged with:
- Error code
- Descriptive message
- Contextual information
- Full stack trace (when available)

## Customization
- Create custom error types by inheriting from `PrometheusBaseError`
- Implement custom error handlers
- Configure logging as needed