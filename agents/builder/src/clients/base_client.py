"""Base client for LLM API implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import os
import importlib.util
from .conversation_manager import ConversationManager
from .types import ToolDefinition, MessageContent, ToolCall


class Client(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(
        self,
        model: Optional[str] = None,
        db_path: Optional[Path] = None,
    ):
        if not db_path:
            db_path = Path(os.getenv("DATABASE_PATH", "./conversations.db"))

        self.storage = ConversationManager(db_path)
        self.model = self._get_default_model() if model is None else model
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_functions: Dict[str, Callable] = {}

    @abstractmethod
    def _get_default_model(self) -> str:
        """Get the default model for this API."""
        pass

    @abstractmethod
    def _convert_tool_to_api_format(self, tool: ToolDefinition) -> Dict[str, Any]:
        """Convert internal tool definition to API-specific format."""
        pass

    @abstractmethod
    def _convert_message_to_api_format(self, message: MessageContent) -> Dict[str, Any]:
        """Convert internal message format to API-specific format."""
        pass

    @abstractmethod
    def _convert_api_response_to_message(self, response: Any) -> MessageContent:
        """Convert API response to internal message format."""
        pass

    @abstractmethod
    def _make_api_call(
        self,
        messages: List[MessageContent],
        system_prompt: Optional[str] = None,
        tools: Optional[List[ToolDefinition]] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """Make API call with standardized parameters."""
        pass

    def register_tools(self, definitions_path: str) -> List[str]:
        """Register tools from a definitions file.

        Args:
            definitions_path: Path to the definitions.py file containing TOOL_DEFINITIONS

        Returns:
            List of registered tool names

        Raises:
            ValueError: If file doesn't exist or doesn't contain TOOL_DEFINITIONS
            ImportError: If module cannot be loaded
            ValueError: If attempting to register a tool that already exists
        """
        path = Path(definitions_path)
        if not path.exists():
            raise ValueError(f"Definitions file not found: {path}")

        # Import the definitions module
        spec = importlib.util.spec_from_file_location("definitions", path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load {path}")

        definitions_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(definitions_module)

        if not hasattr(definitions_module, "TOOL_DEFINITIONS"):
            raise ValueError(f"{path} must contain TOOL_DEFINITIONS dictionary")

        # Check for duplicate tools before registering any
        for tool_name in definitions_module.TOOL_DEFINITIONS:
            if tool_name in self.tools:
                raise ValueError(f"Tool already exists: {tool_name}")

        # Update tools dictionary with new definitions
        self.tools.update(definitions_module.TOOL_DEFINITIONS)
        return list(definitions_module.TOOL_DEFINITIONS.keys())

    def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool and return its response.

        Args:
            tool_call: API-specific tool call format

        Returns:
            Tool execution result as a string
        """
        tool_name = tool_call["name"]
        tool_args = tool_call["arguments"]

        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        return tool["function"](**tool_args)

    def send_message(
        self,
        prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        max_tokens: Optional[int] = 2000,
        tool_response: Optional[str] = None,
        tool_use_id: Optional[str] = None,
    ) -> MessageContent:
        """Send a message using internal formats."""
        if not prompt and not tool_response:
            raise ValueError("Either prompt or tool_response must be provided")

        # Create or get conversation
        if not conversation_id:
            conversation_id = self.storage.create_conversation(self.model)

        # Get conversation details and history
        conv_details = self.storage.get_conversation(conversation_id)
        messages = self.storage.get_messages(conversation_id)

        # Add new message if applicable
        if prompt:
            new_message = {"role": "user", "content": prompt}
            messages.append(new_message)
            self.storage.save_message(conversation_id, "user", prompt)
        elif tool_response and tool_use_id:
            # Format will vary by API implementation
            new_message = self._format_tool_response(tool_response, tool_use_id)
            messages.append(new_message)
            self.storage.save_message(
                conversation_id, new_message["role"], new_message["content"]
            )

        # Make API call
        api_response = self._make_api_call(
            messages=messages,
            system_prompt=conv_details["system_prompt"],
            tools=list(self.tools.values()) if self.tools else None,
            max_tokens=max_tokens,
        )

        # Convert and store response
        response_message = self._convert_api_response_to_message(api_response)
        self.storage.save_message(
            conversation_id, response_message["role"], response_message["content"]
        )

        return response_message
