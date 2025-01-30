"""Module for testing Claude's tool use capabilities."""

import json
import sqlite3
import uuid
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, TypedDict, Callable
from anthropic import Anthropic
from anthropic.types import (
    ToolParam,
    ToolChoiceParam,
    ContentBlockParam,
    ToolUseBlock,
    Message,
)


class MessageContent(TypedDict):
    role: str
    content: List[ContentBlockParam]


class ToolConfig(TypedDict):
    tool_definitions: List[ToolParam]
    tool_choice: ToolChoiceParam


class AnthropicClient:
    def __init__(
        self, api_key: str, model: Optional[str] = None, db_path: Optional[str] = None
    ):
        self.client = self._create_client(api_key)
        self.model = model or "claude-3-5-haiku-latest"
        self.tools = []
        self.tool_functions = {}
        self.db_path = db_path or "conversations.db"
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with necessary tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """
            )

    def create_conversation(self) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (conversation_id, model) VALUES (?, ?)",
                (conversation_id, self.model),
            )
        return conversation_id

    def _get_conversation_messages(self, conversation_id: str) -> List[MessageContent]:
        """Retrieve all messages for a conversation in chronological order."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,),
            )
            messages = []
            for role, content in cursor.fetchall():
                messages.append({"role": role, "content": json.loads(content)})
            return messages

    def _save_message(
        self, conversation_id: str, role: str, content: List[ContentBlockParam]
    ):
        """Save a message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (message_id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), conversation_id, role, json.dumps(content)),
            )

    def _create_client(self, api_key: str):
        """Create a new Anthropic client."""
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
        conversation_id: Optional[str] = None,
        max_tokens: Optional[int] = 1024,
        tool_choice: Optional[ToolChoiceParam] = None,
        tool_response: Optional[str] = None,
        tool_use_id: Optional[str] = None,
    ) -> Message:
        """
        Send a message to Claude, automatically managing conversation history.

        Args:
            prompt: The message to send to Claude
            conversation_id: ID of the conversation to continue. If None, creates a new conversation
            max_tokens: Maximum tokens in the response
            tool_choice: Optional tool choice configuration
            tool_response: Optional response from a previous tool call
            tool_use_id: ID of the tool use when providing a tool response

        Returns:
            Message: Claude's response
        """
        if not prompt and not tool_response:
            raise ValueError("Prompt or tool response must be provided")

        # Create or get conversation
        if not conversation_id:
            conversation_id = self.create_conversation()

        # Get previous messages
        messages = self._get_conversation_messages(conversation_id)

        # Add new message if it's a prompt
        if prompt:
            messages.append({"role": "user", "content": prompt})
            self._save_message(conversation_id, "user", prompt)

        tool_config = self.create_tool_config(tool_choice)

        # Handle tool response
        if tool_response is not None:
            if not tool_use_id:
                raise ValueError("Tool use ID is required")

            response = self.send_message_with_tool_response(
                tool_response,
                tool_use_id,
                tool_config,
                messages,
                max_tokens,
            )
        elif tool_choice is not None:
            response = self.send_message_with_tool(
                messages,
                tool_config,
                max_tokens,
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
            )

        # Save assistant's response
        self._save_message(conversation_id, "assistant", response.content)

        return response

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
