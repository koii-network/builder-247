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
import logging
import json
from typing import Optional, Dict, Any

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
    before=lambda retry_state: (
        retry_state.kwargs.update({"is_retry": True})
        if retry_state.attempt_number > 1
        else None
    ),
)
def execute_tool_with_retry(client, tool_use):
    """Execute tool with retry logic"""
    try:
        logger.info(f"\n=== EXECUTING TOOL: {tool_use.name} ===")
        logger.info(f"Tool input: {json.dumps(tool_use.input, indent=2)}")
        result = client.execute_tool(tool_use)
        logger.info(f"Tool result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if is_retryable_error(e):
            logger.warning(f"Retryable error encountered: {str(e)}")
            raise  # Let retry decorator handle it
        logger.error(f"Non-retryable error encountered: {str(e)}")
        raise  # Re-raise other exceptions


@retry(
    retry=retry_if_exception_type(
        (InternalServerError, APIError, requests.exceptions.RequestException)
    ),
    wait=wait_exponential(multiplier=4, min=1, max=60),
    stop=stop_after_attempt(6),
    before_sleep=lambda retry_state: logger.info(
        f"Attempt {retry_state.attempt_number} failed, retrying in {retry_state.next_action.sleep} seconds..."
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
            is_retry=is_retry,  # Pass is_retry to client to prevent duplicate DB entries
        )

        # Log the response
        logger.info("\n=== CLAUDE RESPONSE ===\n%s", response.content)

        return response

    except Exception as e:
        if isinstance(e, BadRequestError):
            logger.error(f"Invalid message structure: {str(e)}")
            raise
        else:
            logger.error(f"Error sending message: {str(e)}")
            raise
