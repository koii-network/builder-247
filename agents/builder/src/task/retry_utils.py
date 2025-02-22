"""Shared retry utilities for API calls."""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from anthropic import InternalServerError, APIError, APIStatusError, BadRequestError
import requests
import logging

logger = logging.getLogger(__name__)


def is_retryable_error(exception):
    """Check if the error is retryable (e.g. rate limits, server errors)"""
    # Never retry bad requests as they indicate invalid message structure
    if isinstance(exception, BadRequestError):
        return False

    if isinstance(exception, (InternalServerError, APIError)):
        # For Anthropic errors, only retry on server errors (5xx) and overloaded (529)
        if isinstance(exception, APIStatusError):
            return exception.status_code >= 500 or exception.status_code == 429
        return True
    if isinstance(exception, requests.exceptions.RequestException):
        if hasattr(exception.response, "status_code"):
            # Only retry on server errors and rate limits
            status_code = exception.response.status_code
            return status_code >= 500 or status_code == 429
    return False


@retry(
    retry=retry_if_exception_type(
        (InternalServerError, APIError, requests.exceptions.RequestException)
    ),
    wait=wait_exponential(
        multiplier=4, min=1, max=60
    ),  # First retry at 4s, then 8s, 16s, 32s, 60s
    stop=stop_after_attempt(6),  # Initial attempt + 5 retries = 6 total attempts
    before_sleep=lambda retry_state: logger.info(
        f"Attempt {retry_state.attempt_number} failed, retrying in {retry_state.next_action.sleep} seconds..."
    ),
)
def execute_tool_with_retry(client, tool_use):
    """Execute tool with retry logic"""
    try:
        return client.execute_tool(tool_use)
    except Exception as e:
        if is_retryable_error(e):
            logger.warning(f"Retryable error encountered: {str(e)}")
            raise  # Let retry decorator handle it
        logger.error(f"Non-retryable error encountered: {str(e)}")
        raise  # Re-raise other exceptions


def send_message_with_retry(client, **kwargs):
    """Send message with retry logic - no automatic retries for messages to maintain conversation state"""
    try:
        return client.send_message(**kwargs)
    except Exception as e:
        if isinstance(e, BadRequestError):
            logger.error(f"Invalid message structure: {str(e)}")
            raise
        elif is_retryable_error(e):
            logger.error(f"Server error encountered: {str(e)}")
            # For server errors, we should let the caller handle retry logic
            # since they need to maintain conversation state
            raise
        else:
            logger.error(f"Non-retryable error encountered: {str(e)}")
            raise
