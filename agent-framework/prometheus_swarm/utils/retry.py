"""Retry utilities for API calls."""

from typing import Callable, TypeVar
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from prometheus_swarm.utils.logging import log_error
from prometheus_swarm.utils.errors import ClientAPIError

T = TypeVar("T")


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, ClientAPIError):
        # Check if the error has a status code >= 429 (rate limit or server error)
        return error.status_code >= 429
    return False


def with_retry(
    max_attempts: int = 5,
    base_delay: float = 5.0,
    max_delay: float = 60.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add retry logic to a function using tenacity."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            retry=retry_if_exception_type(ClientAPIError),
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=base_delay, max=max_delay),
            before_sleep=lambda retry_state: log_error(
                retry_state.outcome.exception(),
                (
                    f"Retry attempt {retry_state.attempt_number}/{max_attempts}: "
                    f"{retry_state.outcome.exception().status_code} - "
                    f"{str(retry_state.outcome.exception())}"
                ),
                include_traceback=False,
            ),
            reraise=True,
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@with_retry()
def send_message_with_retry(client, *args, **kwargs):
    """Send a message with retry logic for recoverable errors.

    Only retries on rate limits (429) and server errors (500+).
    Client errors (4xx) are not retried as they indicate invalid requests.
    """
    return client.send_message(*args, **kwargs)


@with_retry()
def execute_tool_with_retry(client, tool_use):
    """Execute tool with retry logic.

    Only retries on rate limits (429) and server errors (500+).
    Client errors (4xx) are not retried as they indicate invalid requests.
    """
    return client.execute_tool(tool_use)
