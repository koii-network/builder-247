"""Base client for LLM API implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import importlib.util
from .conversation_manager import ConversationManager
from .types import ToolDefinition, MessageContent, ToolCall, ToolChoice, ToolCallContent
from src.utils.logging import log_section, log_key_value, log_error
from src.utils.errors import ClientAPIError
import json
import ast


class Client(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(
        self,
        model: Optional[str] = None,
    ):
        """Initialize the client."""
        self.storage = ConversationManager()
        self.model = self._get_default_model() if model is None else model
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_functions: Dict[str, Callable] = {}
        self.api_name = self._get_api_name()

    @abstractmethod
    def _get_default_model(self) -> str:
        """Get the default model for this API."""
        pass

    @abstractmethod
    def _get_api_name(self) -> str:
        """Get the name of the API."""
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
        """Register tools from a definitions file."""
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

    @abstractmethod
    def _format_tool_response(self, response: str) -> MessageContent:
        """Format a tool response into a message.

        The response must be a JSON string of [{tool_call_id, response}, ...] representing
        one or more tool results.
        """
        pass

    def _should_split_tool_responses(self) -> bool:
        """Whether to send each tool response as a separate message.

        Override this in client implementations that require separate messages
        for each tool response (e.g. OpenAI).
        """
        return False

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
            conversation_id = self.create_conversation(system_prompt=None)

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
                if self._should_split_tool_responses():
                    # Send each tool response as a separate message
                    results = json.loads(tool_response)
                    for result in results:
                        formatted_response = self._format_tool_response(
                            json.dumps([result])
                        )
                        self.storage.save_message(
                            conversation_id,
                            formatted_response["role"],
                            formatted_response["content"],
                        )
                        messages.append(formatted_response)
                else:
                    # Send all tool responses in one message
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

    def _get_tool_calls(self, msg: MessageContent) -> List[ToolCallContent]:
        """Return all tool call blocks from the message."""
        tool_calls = []
        for block in msg["content"]:
            if block["type"] == "tool_call":
                tool_calls.append(block["tool_call"])
        return tool_calls

    def handle_tool_response(self, response):
        """
        Handle tool responses until natural completion.
        If a tool has final_tool=True and was successful, returns immediately after executing that tool.
        """
        conversation_id = response["conversation_id"]  # Store conversation ID

        while True:
            tool_calls = self._get_tool_calls(response)
            if not tool_calls:
                break  # No more tool calls, we're done

            # Process all tool calls in the current response
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Check if this tool has final_tool set
                    tool_definition = self.tools.get(tool_call["name"])
                    should_return = tool_definition and tool_definition.get(
                        "final_tool", False
                    )

                    # Execute the tool with retry logic
                    tool_output = self.execute_tool(tool_call)

                    # Convert tool output to string if it's not already
                    tool_response_str = (
                        str(tool_output) if tool_output is not None else None
                    )
                    if tool_response_str is None:
                        log_error(
                            Exception("Tool output is None, skipping message to agent"),
                            "Warning",
                        )
                        # Add error response for this tool call
                        tool_results.append(
                            {
                                "tool_call_id": tool_call["id"],
                                "response": str(
                                    {"success": False, "error": "Tool output is None"}
                                ),
                            }
                        )
                        continue

                    # Add to results list
                    tool_results.append(
                        {"tool_call_id": tool_call["id"], "response": tool_response_str}
                    )

                    # If this tool has final_tool=True and was successful, return its result
                    if should_return:
                        try:
                            result = ast.literal_eval(tool_response_str)
                            if isinstance(result, dict) and result.get(
                                "success", False
                            ):
                                return tool_results
                        except (ValueError, SyntaxError):
                            pass  # Continue if we can't parse the response

                except ClientAPIError:
                    # API errors are from our code, so we log them
                    raise

                except Exception as e:
                    # Format error as a string for Claude but don't log it
                    error_response = {
                        "success": False,
                        "error": str(e),
                        "tool_name": tool_call["name"],
                        "input": tool_call["arguments"],
                    }
                    tool_results.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "response": str(error_response),
                        }
                    )

            # Send tool results back to the agent and get next response
            try:
                response = self.send_message(
                    tool_response=json.dumps(tool_results),
                    conversation_id=conversation_id,
                )
            except Exception:
                # Error already logged in _make_api_call
                raise

        # Return the last set of tool results
        return tool_results


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
