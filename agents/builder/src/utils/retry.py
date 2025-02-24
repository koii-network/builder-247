"""Shared retry utilities for API calls."""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from anthropic import InternalServerError, APIError, APIStatusError, BadRequestError
from anthropic.types import Message
import requests
from typing import Optional, Dict, Any
from src.utils.logging import log_error, log_key_value


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
    wait=wait_exponential(multiplier=4, min=1, max=60),
    stop=stop_after_attempt(6),
    before_sleep=lambda retry_state: log_key_value(
        "Retry attempt",
        f"Attempt {retry_state.attempt_number} failed, retrying in {retry_state.next_action.sleep} seconds...",
    ),
    before=lambda retry_state: (
        retry_state.kwargs.update({"is_retry": True})
        if retry_state.attempt_number > 1
        else None
    ),
)
def execute_tool_with_retry(client, tool_use):
    """Execute tool with retry logic"""
    try:
        result = client.execute_tool(tool_use)
        return result
    except Exception as e:
        if is_retryable_error(e):
            log_key_value("Warning", f"Retryable error encountered: {str(e)}")
            raise  # Let retry decorator handle it
        log_error(e, "Non-retryable error encountered", include_traceback=False)
        raise  # Re-raise other exceptions


@retry(
    retry=retry_if_exception_type(
        (InternalServerError, APIError, requests.exceptions.RequestException)
    ),
    wait=wait_exponential(multiplier=4, min=1, max=60),
    stop=stop_after_attempt(6),
    before_sleep=lambda retry_state: log_key_value(
        "Retry attempt",
        f"Attempt {retry_state.attempt_number} failed, retrying in {retry_state.next_action.sleep} seconds...",
    ),
    before=lambda retry_state: (
        retry_state.kwargs.update({"is_retry": True})
        if retry_state.attempt_number > 1
        else None
    ),
)
def send_message_with_retry(
    client,
    prompt: Optional[str] = None,
    conversation_id: Optional[str] = None,
    max_tokens: Optional[int] = 2000,
    tool_choice: Optional[Dict[str, Any]] = None,
    tool_response: Optional[str] = None,
    tool_use_id: Optional[str] = None,
    is_retry: bool = False,
) -> Message:
    """
    Send message with retry logic.

    Args:
        client: The AnthropicClient instance
        prompt: The message to send to Claude
        conversation_id: ID of the conversation to continue
        max_tokens: Maximum tokens in the response
        tool_choice: Optional tool choice configuration
        tool_response: Optional response from a previous tool call
        tool_use_id: ID of the tool use when providing a tool response
        is_retry: Whether this is a retry attempt. If True, won't save new messages to DB.
    """
    try:
        # Send the message
        response = client.send_message(
            prompt=prompt,
            conversation_id=conversation_id,
            max_tokens=max_tokens,
            tool_choice=tool_choice,
            tool_response=tool_response,
            tool_use_id=tool_use_id,
            is_retry=is_retry,
        )

        return response

    except Exception as e:
        if isinstance(e, BadRequestError):
            log_error(e, "Invalid message structure", include_traceback=False)
            raise
        else:
            log_error(e, "Error sending message", include_traceback=False)
            raise
