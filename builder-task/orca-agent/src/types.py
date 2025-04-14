from typing import Dict, Any, Optional, List, TypedDict, Union, Literal, Callable


class ToolDefinition(TypedDict):
    """Standard internal tool definition format."""

    name: str
    description: str
    parameters: Dict[str, str]  # JSON Schema object
    required: List[str]
    final_tool: bool
    function: Callable


class ToolCall(TypedDict):
    """Format for a tool call made by the LLM."""

    id: str  # Unique identifier for this tool call
    name: str  # name of tool being called
    arguments: Dict[str, Any]


class ToolOutput(TypedDict):
    """Standard output format for all tools.

    All tools must return a response in this format.
    The message field contains a human-readable description of what happened,
    which will be an error message if success is False.
    """

    success: bool  # Whether the tool execution was successful
    message: str  # Human-readable message about what happened (error message if success is False)
    data: Optional[Dict[str, Any]]  # Optional structured data from the tool


class ToolResponse(TypedDict):
    """Format for a tool execution response.

    Wraps a tool's output with its call ID for client handling.
    """

    tool_call_id: str  # ID of the tool call this is responding to
    output: ToolOutput  # The actual output from the tool


class PhaseResult(TypedDict):
    """Format for a phase result."""

    success: bool
    data: Dict[str, Any]
    error: Optional[str]


class ToolChoice(TypedDict):
    """Configuration for tool usage."""

    type: Literal["optional", "required", "required_any"]
    tool: Optional[str]  # Required only when type is "required"


class ToolConfig(TypedDict):
    """Configuration for tool usage."""

    tool_definitions: List[ToolDefinition]
    tool_choice: ToolChoice


class TextContent(TypedDict):
    """Format for plain text content."""

    type: Literal["text"]
    text: str


class ToolCallContent(TypedDict):
    """Format for tool call content."""

    type: Literal["tool_call"]
    tool_call: ToolCall


class ToolResponseContent(TypedDict):
    """Format for tool response content."""

    type: Literal["tool_response"]
    tool_response: ToolResponse


class MessageContent(TypedDict):
    """Standard internal message format."""

    role: Literal["user", "assistant", "system", "tool"]
    content: Union[str, List[Union[TextContent, ToolCall, ToolResponseContent]]]


class SuccessResponse(TypedDict):
    """Response for successful operations."""

    success: bool  # Always True
    data: Dict[
        str, Any
    ]  # Can contain any fields needed like message, pr_url, round_number etc.


class ErrorResponse(TypedDict):
    """Response for failed operations."""

    success: bool  # Always False
    status: int
    error: str


ServiceResponse = Union[SuccessResponse, ErrorResponse]
