"""Anthropic/Claude API client implementation."""

from typing import Dict, Any, Optional, List, Union
from anthropic import Anthropic
from anthropic.types import Message, TextBlock, ToolUseBlock
import json
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


class AnthropicClient(Client):
    """Anthropic/Claude API client implementation."""

    def __init__(self, api_key: str, model: Optional[str] = None, **kwargs):
        super().__init__(model=model, **kwargs)
        self.client = Anthropic(api_key=api_key)

    def _get_default_model(self) -> str:
        return "claude-3-haiku-20240307"

    def _convert_tool_to_api_format(self, tool: ToolDefinition) -> Dict[str, Any]:
        """Convert our tool definition to Anthropic's format."""
        return {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["parameters"],
        }

    def _convert_message_to_api_format(self, message: MessageContent) -> Dict[str, Any]:
        """Convert our message format to Anthropic's format."""
        content = message["content"]

        # Map our roles to Anthropic roles
        role = "user" if message["role"] == "tool" else message["role"]

        # Handle string content (convert to text block)
        if isinstance(content, str):
            return {
                "role": role,
                "content": [{"type": "text", "text": content}],
            }

        # Handle list of content blocks
        api_content = []
        for block in content:
            if block["type"] == "text":
                api_content.append({"type": "text", "text": block["text"]})
            elif block["type"] == "tool_call":
                api_content.append(
                    {
                        "type": "tool_use",
                        "id": block["tool_call"]["id"],
                        "name": block["tool_call"]["name"],
                        "input": block["tool_call"]["arguments"],
                    }
                )
            elif block["type"] == "tool_response":
                api_content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["tool_response"]["tool_call_id"],
                        "content": block["tool_response"]["content"],
                    }
                )

        return {"role": role, "content": api_content}

    def _convert_api_response_to_message(self, response: Message) -> MessageContent:
        """Convert Anthropic's response to our message format."""
        content: List[Union[TextContent, ToolCallContent]] = []

        for block in response.content:
            if isinstance(block, TextBlock):
                content.append({"type": "text", "text": block.text})
            elif isinstance(block, ToolUseBlock):
                content.append(
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": block.id,
                            "name": block.name,
                            "arguments": block.input,
                        },
                    }
                )

        return {"role": "assistant", "content": content}

    def _convert_tool_choice_to_api_format(
        self, tool_choice: ToolChoice
    ) -> Dict[str, Any]:
        """Convert our tool choice format to Anthropic's format."""
        # Map our tool choice types to Anthropic's format
        if tool_choice["type"] == "optional":
            return {"type": "auto"}
        elif tool_choice["type"] == "required":
            if not tool_choice.get("tool"):
                raise ValueError("Tool name required when type is 'required'")
            return {"type": "tool", "name": tool_choice["tool"]}
        elif tool_choice["type"] == "required_any":
            return {"type": "any"}
        else:
            raise ValueError(f"Invalid tool choice type: {tool_choice['type']}")

    def _make_api_call(
        self,
        messages: List[MessageContent],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tool_choice: Optional[ToolChoice] = None,
    ) -> Message:
        """Make API call to Anthropic."""
        try:
            # Convert messages and tools to Anthropic format
            api_messages = [
                self._convert_message_to_api_format(msg) for msg in messages
            ]
            api_tools = (
                [self._convert_tool_to_api_format(tool) for tool in self.tools.values()]
                if self.tools
                else None
            )

            # Create API request parameters
            params = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": max_tokens or 2000,
            }
            if system_prompt:
                params["system"] = system_prompt
            if api_tools:
                params["tools"] = api_tools
                if tool_choice:
                    params["tool_choice"] = self._convert_tool_choice_to_api_format(
                        tool_choice
                    )

            # Make API call
            return self.client.messages.create(**params)

        except Exception as e:
            # Only wrap actual API errors
            log_error(
                e,
                context="Error making API call to Anthropic",
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
            "role": "tool",
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

    def send_message(
        self,
        prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tool_choice: Optional[ToolChoice] = None,
        tool_response: Optional[str] = None,
        tool_use_id: Optional[str] = None,
        is_retry: bool = False,
    ) -> Message:
        """Send a message to Claude, automatically managing conversation history."""
        return super().send_message(
            prompt=prompt,
            conversation_id=conversation_id,
            max_tokens=max_tokens,
            tool_choice=tool_choice,
            tool_response=tool_response,
            is_retry=is_retry,
        )
