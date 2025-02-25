"""Base client for LLM API implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import os
import importlib.util
from .conversation_manager import ConversationManager
from .types import ToolDefinition, MessageContent, ToolCall, ToolChoice
from src.utils.logging import log_section, log_key_value
import json
import ast


class Client(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(
        self,
        model: Optional[str] = None,
        db_path: Optional[Path] = None,
    ):
        """Initialize the client."""
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
        max_tokens: Optional[int] = None,
        tool_choice: Optional[ToolChoice] = None,
    ) -> Any:
        """Make API call with standardized parameters."""
        pass

    def register_tools(self, definitions_path: str) -> List[str]:
        """Register tools from a definitions file.

        Args:
            definitions_path: Path to the folder containing the definitions.py file

        Returns:
            List of registered tool names

        Raises:
            ValueError: If file doesn't exist or doesn't contain DEFINITIONS
            ImportError: If module cannot be loaded
            ValueError: If attempting to register a tool that already exists
        """
        path = Path(definitions_path) / "definitions.py"
        if not path.exists():
            raise ValueError(f"Definitions file not found: {path}")

        # Import the definitions module
        spec = importlib.util.spec_from_file_location("definitions", path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load {path}")

        definitions_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(definitions_module)

        if not hasattr(definitions_module, "DEFINITIONS"):
            raise ValueError(f"{path} must contain DEFINITIONS dictionary")

        # Check for duplicate tools before registering any
        for tool_name in definitions_module.DEFINITIONS:
            if tool_name in self.tools:
                raise ValueError(f"Tool already exists: {tool_name}")

        # Update tools dictionary with new definitions
        for name, tool in definitions_module.DEFINITIONS.items():
            self.tools[name] = tool
        return list(definitions_module.DEFINITIONS.keys())

    def create_conversation(self, system_prompt: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        return self.storage.create_conversation(self.model, system_prompt)

    def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool and return its response."""
        tool_name = tool_call["name"]
        tool_args = tool_call["arguments"]

        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Log tool call
        log_section("EXECUTING TOOL")
        log_key_value("Tool", tool_name)
        if tool_args:
            log_key_value("INPUTS:", "")
            for key, value in tool_args.items():
                log_key_value(key, value)

        tool = self.tools[tool_name]
        result = tool["function"](**tool_args)

        # Log result
        log_key_value("RESULT:", "")
        if isinstance(result, dict):
            # Handle success/failure responses
            if "success" in result:
                if result["success"]:
                    log_key_value("Status", "✓ Success")
                    # For successful operations, show the main result or message
                    if "message" in result:
                        log_key_value("Message", result["message"])
                    # Show other relevant fields (excluding success flag and error)
                    for key, value in result.items():
                        if key not in ["success", "error", "message"]:
                            log_key_value(key, value)
                else:
                    log_key_value("Status", "✗ Failed")
                    if "error" in result:
                        log_key_value("Error", result["error"])
            else:
                # For other responses, just show key-value pairs
                for key, value in result.items():
                    log_key_value(key, value)
        else:
            log_key_value("Output", result)

        return result

    def send_message(
        self,
        prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tool_choice: Optional[ToolChoice] = None,
        tool_response: Optional[str] = None,
        is_retry: bool = False,
    ) -> Any:
        """Send a message to the LLM."""
        if not self.storage:
            raise ValueError("Storage not configured - db_path required")

        if not prompt and not tool_response:
            raise ValueError("Prompt or tool response must be provided")

        # Log message being sent
        log_section("SENDING MESSAGE TO AGENT")
        if is_retry:
            log_key_value("Is Retry", "True")
        if conversation_id:
            log_key_value("Conversation ID", conversation_id)
        if prompt:
            log_key_value("PROMPT", prompt)
        if tool_response:
            results = json.loads(tool_response)
            for result in results:
                log_key_value("Tool Use ID", result["tool_call_id"])
                try:
                    response_dict = ast.literal_eval(result["response"])
                    if isinstance(response_dict, dict):
                        if "success" in response_dict:
                            log_key_value(
                                "Status",
                                "✓ Success" if response_dict["success"] else "✗ Failed",
                            )
                            if response_dict.get("message"):
                                log_key_value("Message", response_dict["message"])
                            # Show other fields
                            for key, value in response_dict.items():
                                if key not in ["success", "message"]:
                                    log_key_value(key, value)
                        else:
                            # Just show all key-value pairs
                            for key, value in response_dict.items():
                                log_key_value(key, value)
                    else:
                        log_key_value("Response", result["response"])
                except (ValueError, SyntaxError):
                    log_key_value("Response", result["response"])

        # Create or get conversation
        if not conversation_id:
            conversation_id = self.storage.create_conversation(model=self.model)

        # Get conversation details including system prompt
        conversation = self.storage.get_conversation(conversation_id)
        system_prompt = conversation.get("system_prompt")

        # Get previous messages
        messages = self.storage.get_messages(conversation_id)

        # Add new message if it's a prompt or tool response and not a retry
        if not is_retry:
            if prompt:
                self.storage.save_message(conversation_id, "user", prompt)
                messages.append({"role": "user", "content": prompt})
            elif tool_response:
                formatted_response = self._format_tool_response(tool_response)
                self.storage.save_message(
                    conversation_id,
                    formatted_response["role"],
                    formatted_response["content"],
                )
                messages.append(formatted_response)

        # Make API call
        response = self._make_api_call(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            tool_choice=tool_choice,
        )

        # Convert response to internal format
        converted_response = self._convert_api_response_to_message(response)

        # Log LLM response
        log_section("AGENT'S RESPONSE")
        for block in converted_response["content"]:
            if block["type"] == "text":
                log_key_value("REPLY", block["text"])
            elif block["type"] == "tool_call":
                log_key_value(
                    "TOOL REQUEST",
                    f"{block['tool_call']['name']} (ID: {block['tool_call']['id']})",
                )

        # Add conversation_id to converted response
        converted_response["conversation_id"] = conversation_id

        # Save to storage if not a retry
        if not is_retry:
            self.storage.save_message(
                conversation_id, "assistant", converted_response["content"]
            )

        return converted_response

    @abstractmethod
    def _format_tool_response(self, response: str) -> MessageContent:
        """Format a tool response into a message.

        The response must be a JSON string of [{tool_call_id, response}, ...] representing
        one or more tool results.
        """
        pass


class PreLoggedError(Exception):
    """Error that has already been logged at source.

    Used to wrap API errors that have been logged where they occurred,
    to prevent duplicate logging higher up the stack.
    """

    def __init__(self, original_error: Exception):
        self.original_error = original_error
        super().__init__(str(original_error))

    @property
    def status_code(self) -> int:
        """Preserve status code from original error if it exists."""
        return getattr(self.original_error, "status_code", None)
