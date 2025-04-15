"""Base client for LLM API implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import importlib.util
from .conversation_manager import ConversationManager
from ..types import (
    ToolDefinition,
    MessageContent,
    ToolCall,
    ToolChoice,
    ToolCallContent,
)
from prometheus_swarm.utils.logging import log_section, log_key_value, log_error
from prometheus_swarm.utils.errors import ClientAPIError
from prometheus_swarm.utils.retry import (
    is_retryable_error,
    send_message_with_retry,
    execute_tool_with_retry,
)
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
        self.model = model or self._get_default_model()
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
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make API call to the LLM service.

        This method should be implemented by each client to handle the specifics of their API.
        The base class will handle error logging and wrapping.
        """
        pass

    def make_api_call(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make API call with error handling.

        This method wraps the client-specific _make_api_call with common error handling.
        """
        try:
            # Build kwargs based on what the specific client implementation supports
            kwargs = {
                "messages": messages,
                "system_prompt": system_prompt,
                "max_tokens": max_tokens,
                "tools": tools,
                "tool_choice": tool_choice,
            }

            # Only pass extra_headers to OpenAI-based clients
            if extra_headers:
                kwargs["extra_headers"] = extra_headers

            return self._make_api_call(**kwargs)
        except Exception as e:
            # Only wrap non-ClientAPIError exceptions
            if not isinstance(e, ClientAPIError):
                log_error(
                    e,
                    context=f"Error making API call to {self.api_name}",
                    include_traceback=not is_retryable_error(e),
                )
            raise

    def register_tools(self, tools_dir: str) -> List[str]:
        """Register all tools found in a directory.

        Scans the given directory for all tool definition files (definitions.py)
        and registers all tools found. Tool restrictions can be applied later
        at the conversation level.

        Args:
            tools_dir: Path to directory containing tool definitions

        Returns:
            List of registered tool names
        """
        tools_dir = Path(tools_dir)
        if not tools_dir.exists() or not tools_dir.is_dir():
            raise ValueError(f"Tools directory not found: {tools_dir}")

        registered_tools = []

        # Find all definitions.py files in subdirectories
        for definitions_file in tools_dir.rglob("definitions.py"):
            # Import the definitions module
            spec = importlib.util.spec_from_file_location(
                f"tools.{definitions_file.parent.name}", definitions_file
            )
            if not spec or not spec.loader:
                log_error(
                    ImportError(f"Could not load {definitions_file}"),
                    "Warning: Skipping tool definitions file",
                )
                continue

            try:
                definitions_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(definitions_module)

                if not hasattr(definitions_module, "DEFINITIONS"):
                    log_error(
                        ValueError(
                            f"{definitions_file} must contain DEFINITIONS dictionary"
                        ),
                        "Warning: Skipping tool definitions file",
                    )
                    continue

                # Check for duplicate tools before registering any from this file
                new_tools = definitions_module.DEFINITIONS
                duplicates = set(new_tools.keys()) & set(self.tools.keys())
                if duplicates:
                    log_error(
                        ValueError(f"Duplicate tools found: {duplicates}"),
                        "Warning: Skipping duplicate tools",
                    )
                    # Only register non-duplicate tools from this file
                    new_tools = {
                        name: tool
                        for name, tool in new_tools.items()
                        if name not in duplicates
                    }

                # Register tools
                self.tools.update(new_tools)
                registered_tools.extend(new_tools.keys())

            except Exception as e:
                log_error(
                    e,
                    f"Warning: Failed to load tools from {definitions_file}",
                )
                continue

        return registered_tools

    def create_conversation(
        self,
        system_prompt: Optional[str] = None,
        available_tools: Optional[List[str]] = None,
    ) -> str:
        """Create a new conversation and return its ID.

        Args:
            system_prompt: Optional system prompt for the conversation
            available_tools: Optional list of tool names to restrict this conversation to.
                           If None, all registered tools will be available.
        """
        # Validate tool names if provided
        if available_tools is not None:
            unknown_tools = [t for t in available_tools if t not in self.tools]
            if unknown_tools:
                raise ValueError(f"Unknown tools specified: {unknown_tools}")

        return self.storage.create_conversation(
            model=self.model,
            system_prompt=system_prompt,
            available_tools=available_tools,
        )

    def _get_available_tools(self, conversation_id: str) -> Dict[str, ToolDefinition]:
        """Get the tools available for a specific conversation."""
        conversation = self.storage.get_conversation(conversation_id)
        available_tools = conversation.get("available_tools")

        if available_tools is None:
            return self.tools  # Return all tools if no restrictions

        return {
            name: tool for name, tool in self.tools.items() if name in available_tools
        }

    def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool and return its response."""
        try:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]

            if tool_name not in self.tools:
                return {
                    "success": False,
                    "message": f"Unknown tool: {tool_name}",
                    "data": None,
                }

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
            log_section("TOOL RESULT")
            if isinstance(result, dict):
                # Handle success/failure responses
                if "success" in result:
                    log_key_value(
                        "Status", "✓ Success" if result["success"] else "✗ Failed"
                    )
                    if "message" in result:
                        log_key_value("Message", result["message"])
                    # Show data fields in a more readable format
                    if "data" in result and result["data"]:
                        log_key_value("Details:", "")
                        for key, value in result["data"].items():
                            if isinstance(value, (str, int, float, bool)):
                                # For file content, truncate to 10 lines in logs
                                if (
                                    key == "content"
                                    and isinstance(value, str)
                                    and "\n" in value
                                ):
                                    lines = value.split("\n")
                                    num_lines = len(lines)
                                    if num_lines > 10:
                                        truncated = "\n".join(lines[:10])
                                        truncated += f"\n\n... (truncated {num_lines-10} more lines) ..."
                                        log_key_value(key, truncated)
                                    else:
                                        log_key_value(key, value)
                                else:
                                    log_key_value(key, value)
                            elif isinstance(value, dict):
                                # Format nested dicts more nicely
                                log_key_value(key, json.dumps(value, indent=2))
                            else:
                                log_key_value(key, str(value))
                else:
                    # For other responses, just show key-value pairs
                    for key, value in result.items():
                        log_key_value(key, value)
            else:
                log_key_value("Output", result)

            # For final tools, ensure we have a valid response
            if tool.get("final_tool") and (
                not result or not isinstance(result, dict) or "success" not in result
            ):
                return {
                    "success": False,
                    "message": "Invalid response from final tool",
                    "data": None,
                }

            return result

        except Exception as e:
            # Let ClientAPIError propagate for retry handling
            if isinstance(e, ClientAPIError):
                raise
            # For tool execution errors, log and return error response
            log_key_value("Status", "✗ Failed")
            log_key_value("Error", str(e))
            return {"success": False, "message": str(e), "data": None}

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
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a message to the LLM."""
        if not prompt and not tool_response:
            raise ValueError("Prompt or tool response must be provided")

        # Log message being sent
        log_section(f"SENDING MESSAGE TO {self.api_name}")
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
                    else:
                        log_key_value("Response", result["response"])
                except (ValueError, SyntaxError):
                    log_key_value("Response", result["response"])

        # Create or get conversation
        if not conversation_id:
            conversation_id = self.create_conversation(system_prompt=None)

        # Get conversation details including system prompt
        conversation = self.storage.get_conversation(conversation_id)
        system_prompt = conversation["system_prompt"]

        # Get conversation history
        messages = self.storage.get_messages(conversation_id)

        # Add new message if prompt provided
        if prompt:
            messages.append({"role": "user", "content": prompt})
            if not is_retry:
                self.storage.save_message(conversation_id, "user", prompt)

        # Add tool response if provided
        if tool_response:
            tool_message = self._format_tool_response(tool_response)
            if self._should_split_tool_responses():
                # Some APIs (e.g. OpenAI) require separate messages for each tool response
                results = json.loads(tool_response)
                for result in results:
                    messages.append(
                        {
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
                    )
            else:
                messages.append(tool_message)

            if not is_retry:
                self.storage.save_message(
                    conversation_id, "tool", tool_message["content"]
                )

        try:
            # Convert messages to API format
            api_messages = [
                self._convert_message_to_api_format(msg) for msg in messages
            ]

            # Get available tools for this conversation
            available_tools = (
                self._get_available_tools(conversation_id)
                if conversation_id and self.tools
                else self.tools
            )

            # Convert tools to API format
            api_tools = (
                [
                    self._convert_tool_to_api_format(tool)
                    for tool in available_tools.values()
                ]
                if available_tools
                else None
            )

            # Validate tool_choice against available tools
            if tool_choice and tool_choice.get("type") == "required":
                tool_name = tool_choice.get("tool")
                if tool_name and tool_name not in available_tools:
                    raise ValueError(
                        f"Required tool {tool_name} not available in this conversation"
                    )

            # Convert tool choice to API format
            api_tool_choice = (
                self._convert_tool_choice_to_api_format(tool_choice)
                if tool_choice and api_tools
                else None
            )

            # Make API call - errors will already be wrapped in ClientAPIError
            response = self.make_api_call(
                messages=api_messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                tools=api_tools,
                tool_choice=api_tool_choice,
                extra_headers=extra_headers,
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

        except Exception as e:
            # Let ClientAPIError propagate for retry handling
            if isinstance(e, ClientAPIError):
                raise
            # Wrap other unexpected errors
            log_error(
                e, context="Unexpected error in send_message", include_traceback=True
            )
            raise

    def _get_tool_calls(self, msg: MessageContent) -> List[ToolCallContent]:
        """Return all tool call blocks from the message."""
        tool_calls = []
        for block in msg["content"]:
            if block["type"] == "tool_call":
                tool_calls.append(block["tool_call"])
        return tool_calls

    def handle_tool_response(self, response, context: Dict[str, Any]):
        """
        Handle tool responses until natural completion.
        If a tool has final_tool=True and was successful, returns immediately after executing that tool.
        Otherwise continues until the agent has no more tool calls.
        """
        conversation_id = response["conversation_id"]
        last_results = []  # Track the most recent results
        MAX_ITERATIONS = 500
        for _ in range(MAX_ITERATIONS):
            tool_calls = self._get_tool_calls(response)
            if not tool_calls:
                # No more tool calls, return the last results we got
                return last_results

            # Process all tool calls in the current response
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Update tool arguments with context
                    tool_call["arguments"].update(context)
                    # Execute the tool with retry
                    result = execute_tool_with_retry(self, tool_call)
                    if not result:
                        result = {
                            "success": False,
                            "message": "Tool output is None",
                            "data": None,
                        }

                    # Add result to tool_results
                    tool_results.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "response": str(result),
                        }
                    )

                    # Only return early for successful final tools
                    is_final_tool = self.tools[tool_call["name"]].get(
                        "final_tool", False
                    )
                    if is_final_tool and result.get("success", False):
                        return [tool_results[-1]]
                    # For failed final tools, continue processing to let agent try again

                except Exception as e:
                    # Log the error and add it to tool results
                    log_error(e, f"Error executing tool {tool_call['name']}")
                    tool_results.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "response": str(
                                {
                                    "success": False,
                                    "message": str(e),
                                    "data": None,
                                }
                            ),
                        }
                    )

            # Update last_results with current results
            last_results = tool_results

            # Send tool results to agent and get next response
            response = send_message_with_retry(
                self,
                conversation_id=conversation_id,
                tool_response=json.dumps(tool_results),
            )
