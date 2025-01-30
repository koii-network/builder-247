"""Module for testing Claude's tool use capabilities."""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, TypedDict, Callable
from anthropic import Anthropic
from anthropic.types import (
    ToolParam,
    ToolChoiceParam,
    ContentBlockParam,
    ToolUseBlock,
)


class MessageContent(TypedDict):
    role: str
    content: List[ContentBlockParam]


class ToolConfig(TypedDict):
    tool_definitions: List[ToolParam]
    tool_choice: ToolChoiceParam


class AnthropicClient:
    def __init__(self, model: Optional[str] = None):
        self.client = self.create_client()
        self.model = model or "claude-3-5-haiku-latest"
        self.tools = []
        self.tool_functions = {}

    def create_client(self):
        """Create a new Anthropic client."""
        api_key = os.environ.get("CLAUDE_API_KEY")

        if not api_key:
            raise ValueError("Missing CLAUDE_API_KEY")

        return Anthropic(api_key=api_key)

    def create_tool_config(
        self,
        tool_choice: Optional[ToolChoiceParam] = None,
    ) -> ToolConfig:
        tool_choice = tool_choice or {"type": "auto"}
        return ToolConfig(tool_definitions=self.tools, tool_choice=tool_choice)

    def register_tool(self, tool_definition: ToolParam, tool_function: Callable) -> str:
        """Register a single tool with its implementation."""
        self.tools.append(tool_definition)
        self.tool_functions[tool_definition["name"]] = tool_function
        return tool_definition["name"]

    def register_tools_from_directory(self, definitions_dir: str) -> List[str]:
        """Register multiple tools from a directory containing tool definitions and implementations.

        The directory should contain:
        - JSON files defining each tool
        - An implementations.py file that exports a TOOL_IMPLEMENTATIONS dictionary mapping
          tool names to their implementation functions

        Args:
            definitions_dir: Path to directory containing tool definitions and implementations

        Returns:
            List of registered tool names

        Raises:
            ValueError: If directory not found or missing implementations.py
            ImportError: If implementations.py cannot be loaded
        """
        registered_tools = []
        definitions_path = Path(definitions_dir)

        if not definitions_path.exists() or not definitions_path.is_dir():
            raise ValueError(f"Directory not found: {definitions_dir}")

        # Load implementations from implementations.py
        impl_path = definitions_path / "implementations.py"
        if not impl_path.exists():
            raise ValueError(f"Missing implementations.py in {definitions_dir}")

        # Import the implementations module
        spec = importlib.util.spec_from_file_location("implementations", impl_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load {impl_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "TOOL_IMPLEMENTATIONS"):
            raise ValueError(
                "implementations.py must export TOOL_IMPLEMENTATIONS dictionary"
            )

        implementations = module.TOOL_IMPLEMENTATIONS

        # Register each tool
        for definition_file in definitions_path.glob("*.json"):
            with open(definition_file) as f:
                tool_definition = json.load(f)

            tool_name = tool_definition["name"]
            if tool_name not in implementations:
                raise ValueError(f"Missing implementation for tool: {tool_name}")

            registered_tools.append(
                self.register_tool(tool_definition, implementations[tool_name])
            )

        return registered_tools

    def send_message(
        self,
        prompt: Optional[str] = None,
        previous_messages: Optional[List[MessageContent]] = None,
        max_tokens: Optional[int] = 1024,
        tool_choice: Optional[ToolChoiceParam] = None,
        tool_response: Optional[str] = None,
        tool_use_id: Optional[str] = None,
    ) -> str:
        """
        Send a test message to Claude via the Anthropic API.

        Args:
            message (str): Message to send to Claude. Defaults to a test message.

        Returns:
            str: Claude's response

        Raises:
            ValueError: If CLAUDE_API_KEY is not set
        """

        if not prompt and not tool_response:
            raise ValueError("Prompt or tool response must be provided")

        messages = previous_messages or []

        if prompt:
            messages.append({"role": "user", "content": prompt})

        tool_config = self.create_tool_config(tool_choice)

        if tool_response is not None:
            if not tool_use_id:
                raise ValueError("Tool use ID is required")

            if not previous_messages:
                raise ValueError("A previous message with the tool call is required")

            return self.send_message_with_tool_response(
                tool_response,
                tool_use_id,
                tool_config,
                previous_messages,
                max_tokens,
            )
        if tool_choice is not None:
            return self.send_message_with_tool(
                messages,
                tool_config,
                max_tokens,
            )

        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )

    def send_message_with_tool(
        self,
        messages: List[MessageContent],
        tool_config: ToolConfig,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Send a message to Claude with a tool definition and receive a tool call response.

        Args:
            message (str): Message to send to Claude
            tool_definition (Dict[str, Any]): The tool definition in JSON format
            tool_choice (Optional[Dict[str, str]]): Optional tool choice configuration

        Returns:
            Dict[str, Any]: Claude's response including any tool calls

        Raises:
            ValueError: If CLAUDE_API_KEY is not set
        """

        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tool_config["tool_definitions"],
            tool_choice=tool_config["tool_choice"],
        )

    def send_message_with_tool_response(
        self,
        tool_response: str,
        tool_use_id: str,
        tool_config: ToolConfig,
        previous_messages: List[MessageContent],
        max_tokens: int,
    ):
        """
        Send a message to Claude with a tool call response.
        """

        messages = previous_messages or []

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": [{"type": "text", "text": tool_response}],
                    }
                ],
            }
        )

        print(messages)

        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tool_config["tool_definitions"],
            tool_choice=tool_config["tool_choice"],
        )

    def execute_tool(self, tool_call: ToolUseBlock) -> str:
        tool_function = self.tool_functions[tool_call.name]
        tool_result = tool_function(**tool_call.args)
        return tool_result
