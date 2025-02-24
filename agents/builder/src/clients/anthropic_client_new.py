"""Anthropic/Claude API client implementation."""

from typing import Dict, Any, Optional, List, Union
from anthropic import Anthropic
from anthropic.types import Message, TextBlock, ToolUseBlock
import ast
from .base_client import Client
from .types import ToolDefinition, MessageContent, TextContent, ToolCallContent


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
            "parameters": {
                "type": "object",
                "properties": tool["input_schema"],
                "required": tool["required"],
            },
        }

    def _convert_message_to_api_format(self, message: MessageContent) -> Dict[str, Any]:
        """Convert our message format to Anthropic's format."""
        content = message["content"]

        # Handle string content (convert to text block)
        if isinstance(content, str):
            return {
                "role": message["role"],
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
                        "type": "tool_calls",
                        "tool_calls": [
                            {
                                "id": block["tool_call"]["id"],
                                "name": block["tool_call"]["name"],
                                "parameters": block["tool_call"]["arguments"],
                            }
                        ],
                    }
                )
            elif block["type"] == "tool_response":
                api_content.append(
                    {
                        "type": "tool_response",
                        "tool_call_id": block["tool_response"]["tool_call_id"],
                        "content": block["tool_response"]["content"],
                    }
                )

        return {"role": message["role"], "content": api_content}

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

    def _make_api_call(
        self,
        messages: List[MessageContent],
        system_prompt: Optional[str] = None,
        tools: Optional[List[ToolDefinition]] = None,
        max_tokens: Optional[int] = None,
    ) -> Message:
        """Make API call to Anthropic."""
        # Convert messages and tools to Anthropic format
        api_messages = [self._convert_message_to_api_format(msg) for msg in messages]
        api_tools = (
            [self._convert_tool_to_api_format(tool) for tool in tools]
            if tools
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

        # Make API call
        return self.client.messages.create(**params)

    def _format_tool_response(self, response: str, tool_call_id: str) -> MessageContent:
        """Format a tool response into a message."""
        try:
            # Try to parse as Python dict string
            response_dict = ast.literal_eval(response)
            if isinstance(response_dict, dict):
                content = str(response_dict)
            else:
                content = response
        except (ValueError, SyntaxError):
            content = response

        return {
            "role": "tool",
            "content": [
                {
                    "type": "tool_response",
                    "tool_response": {"tool_call_id": tool_call_id, "content": content},
                }
            ],
        }
