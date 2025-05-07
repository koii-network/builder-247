"""Error types for API and nonce-related errors."""

import logging
import time
from functools import wraps
from typing import Optional, Callable, Any, Union


class ClientAPIError(Exception):
    """Error for API calls with status code."""

    def __init__(self, original_error: Exception):
        print(original_error)
        if hasattr(original_error, "status_code"):
            self.status_code = original_error.status_code
        else:
            self.status_code = 500
        if hasattr(original_error, "message"):
            super().__init__(original_error.message)
        else:
            super().__init__(str(original_error))


class NonceError(Exception):
    """Raised when a nonce (number used once) is invalid or has been reused."""

    def __init__(self, message: str, current_nonce: Optional[str] = None):
        """
        Initialize NonceError with a descriptive message and optional current nonce.

        Args:
            message (str): Description of the nonce error
            current_nonce (Optional[str]): The problematic nonce value
        """
        self.current_nonce = current_nonce
        super().__init__(message)


def nonce_error_handler(
    func: Optional[Callable] = None,
    *,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    logger: Optional[logging.Logger] = None
) -> Union[Callable, Any]:
    """
    Decorator to handle nonce-related errors with automatic recovery and retries.

    Args:
        func (Optional[Callable]): The function to wrap
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay between retry attempts in seconds
        logger (Optional[logging.Logger]): Logger for tracking retry attempts

    Returns:
        Wrapped function with nonce error handling
    """
    def decorator(func_to_wrap: Callable) -> Callable:
        @wraps(func_to_wrap)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func_to_wrap(*args, **kwargs)
                except NonceError as e:
                    retries += 1
                    if logger:
                        logger.warning(
                            f"Nonce error encountered: {e}. "
                            f"Retry attempt {retries}/{max_retries}"
                        )
                    
                    if retries >= max_retries:
                        raise
                    
                    time.sleep(retry_delay * (2 ** retries))  # Exponential backoff
            
            raise RuntimeError("Max nonce error retries exceeded")
        
        return wrapper

    # Support using decorator with or without arguments
    if func is None:
        return decorator
    return decorator(func)