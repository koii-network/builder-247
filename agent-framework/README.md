# Prometheus Swarm Framework

## Error Handling and Logging

### Error Handling Improvements

The `prometheus_swarm/utils/errors.py` module provides enhanced error handling with the following features:

#### Custom Error Types
- `BasePrometheusError`: Base class for all custom errors
- `ClientAPIError`: Detailed errors for API call failures
- `ConfigurationError`: Errors related to configuration issues
- `ResourceAccessError`: Errors when accessing external resources

#### Key Improvements
- Comprehensive error context tracking
- Standardized error response generation
- Detailed traceback and metadata capture

### Logging Enhancements

The `prometheus_swarm/utils/logging.py` module offers advanced logging capabilities:

#### New Logging Functions
- `log_error_details()`: Provides comprehensive error logging
- `log_with_timing()`: Decorator for logging function execution times and details

#### Features
- Colorized console output
- Detailed error context logging
- Execution time tracking
- Flexible logging configuration

### Usage Example

```python
from prometheus_swarm.utils.errors import ClientAPIError, handle_error
from prometheus_swarm.utils.logging import log_with_timing

@log_with_timing
def make_api_call():
    try:
        # Your API call logic
        pass
    except Exception as e:
        raise ClientAPIError(
            original_error=e, 
            message="API call failed", 
            status_code=500
        )

# Error handling
try:
    result = make_api_call()
except Exception as e:
    error_response = handle_error(e)
    print(error_response)
```

### Best Practices
- Use custom error types for precise error tracking
- Leverage logging decorators for comprehensive tracing
- Include meaningful context in error messages