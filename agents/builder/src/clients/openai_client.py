"""OpenAI API client implementation."""

from typing import Dict, Any, Optional, List, Union
from openai import OpenAI
from .base_client import Client
from .types import (
    ToolDefinition,
    MessageContent,
    TextContent,
    ToolCallContent,
    ToolChoice,
)
from src.utils.retry import is_retryable_error
from src.utils.logging import log_error
from src.utils.errors import ClientAPIError
import json


class OpenAIClient(Client):
    """OpenAI API client implementation."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,  # Use default OpenAI URL if not specified
        )

    def _get_api_name(self) -> str:
        """Get API name for logging."""
        return "OpenAI"

    def _get_default_model(self) -> str:
        return "gpt-4-turbo-preview"

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
        content = message["content"]

        # Handle string content
        if isinstance(content, str):
            return {
                "role": message["role"],
                "content": content,
            }

        # Handle list of content blocks
        api_content = ""
        function_call = None
        tool_calls = []

        for block in content:
            if block["type"] == "text":
                api_content += block["text"]
            elif block["type"] == "tool_call":
                tool_calls.append(
                    {
                        "id": block["tool_call"]["id"],
                        "function": {
                            "name": block["tool_call"]["name"],
                            "arguments": json.dumps(block["tool_call"]["arguments"]),
                        },
                    }
                )
            elif block["type"] == "tool_response":
                return {
                    "role": "function",
                    "content": block["tool_response"]["content"],
                    "name": block["tool_response"]["tool_call_id"],
                }

        message_dict = {"role": message["role"]}
        if api_content:
            message_dict["content"] = api_content
        if tool_calls:
            message_dict["tool_calls"] = tool_calls
        if function_call:
            message_dict["function_call"] = function_call

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
        """Convert our tool choice format to OpenAI's format.

        Our format:
        - {"type": "optional"} -> "auto"
        - {"type": "required", "tool": "my_tool"} -> {"type": "function", "function": {"name": "my_tool"}}
        """
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
        messages: List[MessageContent],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tool_choice: Optional[ToolChoice] = None,
    ) -> Dict[str, Any]:
        """Make API call to OpenAI."""
        try:
            # Convert messages and tools to OpenAI format
            api_messages = [
                self._convert_message_to_api_format(msg) for msg in messages
            ]

            # Add system message if provided
            if system_prompt:
                api_messages.insert(0, {"role": "system", "content": system_prompt})

            # Create API request parameters
            params = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": max_tokens or 2000,
            }

            # Add tools if available
            if self.tools:
                params["tools"] = [
                    self._convert_tool_to_api_format(tool)
                    for tool in self.tools.values()
                ]
                # Add tool_choice if specified
                if tool_choice:
                    params["tool_choice"] = self._convert_tool_choice_to_api_format(
                        tool_choice
                    )

            # Make API call
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message

        except Exception as e:
            # Only wrap actual API errors
            log_error(
                e,
                context=f"Error making API call to {self._get_api_name()}",
                include_traceback=not is_retryable_error(e),
            )
            raise ClientAPIError(e)

    def _format_tool_response(self, response: str) -> MessageContent:
        """Format a tool response into a message.

        The response must be a JSON string of [{tool_call_id, response}, ...] representing
        one or more tool results.
        """
        results = json.loads(response)
        return {
            "role": "function",  # OpenAI uses 'function' role for responses
            "content": [
                {
                    "type": "tool_response",
                    "tool_response": {
                        "tool_call_id": result["tool_call_id"],
                        "content": result["response"],
                    },
                }
                for result in results
            ],
        }
