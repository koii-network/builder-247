"""Retry utilities for API calls."""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
    wait_chain,
)
from prometheus_swarm.utils.logging import log_key_value
from src.utils.errors import ClientAPIError


def is_retryable_error(e: Exception) -> bool:
    """Check if an error is retryable.

    An error is considered retryable if it has a status_code attribute >= 429
    (rate limits and server errors).
    """
    return isinstance(e, ClientAPIError) and e.status_code >= 429


def with_retry(func_name: str, max_attempts: int = 6):
    """Decorator factory for retry logic.

    Args:
        func_name: Name of the function being retried (for logging)
        max_attempts: Maximum number of retry attempts
    """

    def decorator(func):
        @retry(
            retry=is_retryable_error,
            # Add a fixed 1 second delay between all API calls, then use exponential backoff for retries
            wait=wait_chain(
                # Always wait at least 10 seconds between calls
                wait_fixed(10),
                # On retries, use exponential backoff starting at 20 seconds
                wait_exponential(multiplier=2, min=20, max=80),
            ),
            stop=stop_after_attempt(max_attempts),
            before_sleep=lambda retry_state: log_key_value(
                "Retry attempt",
                f"{func_name}: Attempt {retry_state.attempt_number} failed, "
                f"retrying in {retry_state.next_action.sleep} seconds...",
            ),
            before=lambda retry_state: (
                retry_state.kwargs.update({"is_retry": True})
                if retry_state.attempt_number > 1
                else None
            ),
        )
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Only wrap API-related errors
                if isinstance(e, ClientAPIError):
                    raise ClientAPIError(e)
                raise  # Let other errors propagate normally

        return wrapper

    return decorator


@with_retry("send_message")
def send_message_with_retry(client, *args, **kwargs):
    """Send a message with retry logic for recoverable errors.

    Only retries on rate limits (429) and server errors (500+).
    Client errors (4xx) are not retried as they indicate invalid requests.
    """
    return client.send_message(*args, **kwargs)


@with_retry("execute_tool")
def execute_tool_with_retry(client, tool_use):
    """Execute tool with retry logic.

    Only retries on rate limits (429) and server errors (500+).
    Client errors (4xx) are not retried as they indicate invalid requests.
    """
    return client.execute_tool(tool_use)
