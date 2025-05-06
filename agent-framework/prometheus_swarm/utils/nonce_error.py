import logging
from typing import Optional, Any, Callable
from functools import wraps
import time
import inspect

class NonceError(Exception):
    """Custom exception for Nonce-related errors."""
    def __init__(self, message: str, nonce: Optional[str] = None):
        """
        Initialize a NonceError with an optional nonce.

        Args:
            message (str): Error message describing the nonce issue
            nonce (Optional[str], optional): The problematic nonce value. Defaults to None.
        """
        self.nonce = nonce
        super().__init__(message)

def validate_nonce(nonce: Optional[str]) -> bool:
    """
    Validate a given nonce.

    Args:
        nonce (Optional[str]): The nonce to validate

    Returns:
        bool: True if nonce is valid, False otherwise
    """
    if nonce is None:
        return False
    
    # Add additional nonce validation logic here (e.g., length, format, etc.)
    return len(str(nonce)) > 0 and len(str(nonce)) <= 64

def handle_nonce_error(
    max_retries: int = 3, 
    retry_delay: float = 1.0, 
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for handling nonce-related errors with retry mechanism.

    Args:
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        retry_delay (float, optional): Delay between retry attempts in seconds. Defaults to 1.0.
        logger (Optional[logging.Logger], optional): Logger for tracking retries. Defaults to None.

    Returns:
        Callable: Decorated function with nonce error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0
            
            # Inspect function signature to find nonce parameter
            sig = inspect.signature(func)
            nonce_param = None
            for param_name, param in sig.parameters.items():
                if param_name == 'nonce':
                    nonce_param = kwargs.get(param_name)
                    break
            
            # Fallback to first positional argument if no keyword 'nonce'
            if nonce_param is None and len(args) > 0:
                nonce_param = args[0]
            
            while retry_count < max_retries:
                try:
                    # Validate nonce before function execution
                    if not validate_nonce(nonce_param):
                        raise NonceError(f"Invalid nonce: {nonce_param}")
                    
                    # Inject validated nonce into arguments if needed
                    if nonce_param is not None:
                        if 'nonce' in sig.parameters:
                            kwargs['nonce'] = nonce_param
                        elif len(args) > 0:
                            args = (nonce_param,) + args[1:]
                    
                    result = func(*args, **kwargs)
                    return result
                
                except (NonceError, ValueError) as e:
                    if logger:
                        logger.warning(f"Nonce error on attempt {retry_count + 1}: {e}")
                    
                    retry_count += 1
                    
                    if retry_count >= max_retries:
                        if logger:
                            logger.error(f"Max retries reached. Nonce error: {e}")
                        raise
                    
                    # Exponential backoff with jitter
                    time.sleep(retry_delay * (2 ** retry_count) + (retry_delay * 0.1 * retry_count))
            
            raise NonceError("Unexpected error in nonce handling")
        
        return wrapper
    
    return decorator