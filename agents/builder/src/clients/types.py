from typing import Dict, Any, Optional, List, TypedDict, Union, Literal, Callable


class ToolDefinition(TypedDict):
    """Standard internal tool definition format."""

    name: str
    description: str
    parameters: Dict[str, str]  # JSON Schema object
    required: List[str]
    return_value: bool
    function: Callable


class ToolCall(TypedDict):
    """Format for a tool call made by the LLM."""

    id: str  # Unique identifier for this tool call
    name: str  # name of tool being called
    arguments: Dict[str, Any]


class ToolResponse(TypedDict):
    """Format for a tool execution response."""

    tool_call_id: str  # ID of the tool call this is responding to
    success: bool  # whether the tool call was successful
    content: str  # output of the tool call


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
