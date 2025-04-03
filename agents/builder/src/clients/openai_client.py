"""OpenAI API client implementation."""

from typing import Dict, Any, Optional, List, Union
from openai import OpenAI
from .base_client import Client
from ..types import (
    ToolDefinition,
    MessageContent,
    TextContent,
    ToolCallContent,
    ToolChoice,
)
import json


class OpenAIClient(Client):
    """OpenAI API client implementation."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,  # Use default OpenAI URL if not specified
        )
        self.default_headers = default_headers

    def _get_api_name(self) -> str:
        """Get API name for logging."""
        return "OpenAI"

    def _get_default_model(self) -> str:
        return "gpt-4o-mini"

    def _should_split_tool_responses(self) -> bool:
        """OpenAI requires separate messages for each tool response."""
        return True

    def _convert_tool_to_api_format(self, tool: ToolDefinition) -> Dict[str, Any]:
        """Convert our tool definition to OpenAI's function format."""
        return {
            "type": "function",  # OpenAI requires this field
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }

    def _convert_message_to_api_format(self, message: MessageContent) -> Dict[str, Any]:
        """Convert our message format to OpenAI's format."""
        # Handle missing content (e.g. in tool responses)
        content = message["content"]

        # Handle string content
        if isinstance(content, str):
            # If this is a tool response message, parse it
            if message["role"] == "tool":
                try:
                    # Try parsing as a list of tool responses first
                    parsed = json.loads(content)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        # Get first tool response
                        result = parsed[0]
                        return {
                            "role": "tool",
                            "tool_call_id": result["tool_call_id"],
                            "content": result["response"],
                        }
                except (json.JSONDecodeError, KeyError):
                    pass
            # Otherwise treat as normal text content
            return {
                "role": message["role"],
                "content": content,
            }

        # Handle list of content blocks
        api_content = ""
        tool_calls = []

        for block in content:
            if block["type"] == "text":
                api_content += block["text"]
            elif block["type"] == "tool_call":
                tool_calls.append(
                    {
                        "type": "function",  # OpenAI requires this field
                        "id": block["tool_call"]["id"],
                        "function": {
                            "name": block["tool_call"]["name"],
                            "arguments": json.dumps(block["tool_call"]["arguments"]),
                        },
                    }
                )
            elif block["type"] == "tool_response":
                # For tool responses, we need to include tool_call_id
                return {
                    "role": "tool",  # OpenAI uses 'tool' role
                    "tool_call_id": block["tool_response"][
                        "tool_call_id"
                    ],  # Required by OpenAI
                    "content": block["tool_response"]["content"],
                }

        message_dict = {"role": message["role"]}
        if api_content:
            message_dict["content"] = api_content
        if tool_calls:
            message_dict["tool_calls"] = tool_calls

        return message_dict

    def _convert_api_response_to_message(self, response: Any) -> MessageContent:
        """Convert OpenAI's response to our message format."""
        content: List[Union[TextContent, ToolCallContent]] = []

        # Handle text content
        if hasattr(response, "content") and response.content:
            content.append({"type": "text", "text": response.content})

        # Handle tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                content.append(
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments),
                        },
                    }
                )

        return {"role": "assistant", "content": content}

    def _convert_tool_choice_to_api_format(
        self, tool_choice: ToolChoice
    ) -> Dict[str, Any]:
        """Convert our tool choice format to OpenAI's format."""
        if tool_choice["type"] == "optional":
            return "auto"
        elif tool_choice["type"] == "required":
            if not tool_choice.get("tool"):
                raise ValueError("Tool name required when type is 'required'")
            return {"type": "function", "function": {"name": tool_choice["tool"]}}
        else:
            raise ValueError(f"Invalid tool choice type: {tool_choice['type']}")

    def _make_api_call(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make API call to OpenAI."""
        # Add system message if provided
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        # Create API request parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or 2000,
        }

        # Add tools if available
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice

        # Add extra headers if we have them
        if extra_headers:
            params["extra_headers"] = extra_headers
        elif self.default_headers:
            params["extra_headers"] = self.default_headers

        # Make API call
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message

    def _format_tool_response(self, response: str) -> MessageContent:
        """Format a tool response into a message.

        The response must be a JSON string of [{tool_call_id, response}, ...] representing
        one or more tool results.

        For OpenAI, each tool response must be a separate message with its own tool_call_id.
        """
        results = json.loads(response)
        # Return just the first tool response - the client will handle sending each one
        result = results[0]  # Take first result
        return {
            "role": "tool",
            "content": [
                {
                    "type": "tool_response",
                    "tool_response": {
                        "tool_call_id": result["tool_call_id"],
                        "content": result["response"],
                    },
                }
            ],
        }
