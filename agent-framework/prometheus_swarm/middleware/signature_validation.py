"""Signature Validation Middleware for request validation."""

from functools import wraps
from typing import Callable, Dict, Any, Optional
from prometheus_swarm.utils.signatures import verify_and_parse_signature
from prometheus_swarm.utils.logging import log_error

def validate_signature(
    staking_key_getter: Optional[Callable[..., str]] = None,
    expected_values: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Create a middleware decorator for signature validation.

    Args:
        staking_key_getter (Optional[Callable]): A function to retrieve the staking key.
            If not provided, the signature will be taken from the first argument.
        expected_values (Optional[Dict]): Dictionary of expected values to validate in the payload.

    Returns:
        Callable: A decorator for signature validation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine the signed_message and staking_key
            if staking_key_getter:
                signed_message = args[0] if len(args) > 0 else kwargs.get('signed_message')
                staking_key = staking_key_getter(*args, **kwargs)
            else:
                # Assume the first argument is signed_message and second is staking_key
                signed_message = args[0] if len(args) > 0 else kwargs.get('signed_message')
                staking_key = args[1] if len(args) > 1 else kwargs.get('staking_key')

            # Validate signature
            result = verify_and_parse_signature(
                signed_message=signed_message,
                staking_key=staking_key,
                expected_values=expected_values
            )

            # Check for verification errors
            if 'error' in result:
                log_error(
                    Exception("Signature Validation Failed"),
                    context=result['error']
                )
                raise ValueError(result['error'])

            # If verification succeeds, replace the signed_message with the decoded data
            # and call the original function
            new_args = list(args)
            if len(new_args) > 0:
                new_args[0] = result['data']
            else:
                kwargs['signed_message'] = result['data']

            return func(*new_args, **kwargs)
        return wrapper
    return decorator