# AnthropicClient API Documentation

## Overview

The `AnthropicClient` class provides a Python interface for interacting with the Anthropic Claude 3 API, with enhanced features for conversation management, token handling, and tool integration.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

The client requires an Anthropic API key, which can be provided in two ways:

1. Environment variable: `ANTHROPIC_API_KEY`
2. Constructor parameter: `api_key`

## Basic Usage

```python
from src.client import AnthropicClient

# Initialize client
client = AnthropicClient(
    api_key="your-api-key",
    model="claude-3-opus-20240229",
    max_tokens=100000,
    history_dir="./history"
)

# Send a message
response_text, tool_calls = client.send_message("Hello, how are you?")
print(response_text)
```

## Class Reference

### Constructor

```python
def __init__(
    self,
    api_key: str,
    model: str = "claude-3-opus-20240229",
    max_tokens: int = 100000,
    history_dir: Optional[str | Path] = None,
)
```

- `api_key`: Anthropic API key
- `model`: Model to use (defaults to Claude 3 Opus)
- `max_tokens`: Maximum tokens in conversation window
- `history_dir`: Optional directory for conversation history
- Raises `ValueError` if no API key is found

### Methods

#### send_message

```python
def send_message(
    self,
    message: str,
    with_history: bool = True,
) -> Tuple[str, List[Dict[str, Any]]]
```

Sends a message to Claude and returns the response with any tool calls.

- `message`: The user's message to send
- `with_history`: Whether to include conversation history
- Returns: Tuple of (response text, list of tool calls)
- Raises: Various exceptions for API errors

### Classes

#### Message

```python
@dataclass
class Message:
    role: str
    content: str
    token_count: Optional[int] = None
```

Represents a message in the conversation.

- Automatically calculates token count if not provided
- Supports serialization to/from dictionary

#### ConversationWindow

```python
class ConversationWindow:
    def __init__(self, max_tokens: int)
    def add_message(self, message: Message) -> None
    def clear(self) -> None
    @property
    def total_tokens(self) -> int
```

Manages conversation window with token limit.

- Tracks total tokens
- Enforces maximum token limit
- Handles message addition/removal

## History Management

The client supports persistent conversation history:

- SQLite-based storage
- Automatic message tracking
- Token count preservation
- Conversation metadata

## Error Handling

The client handles various error conditions:

- API errors (rate limits, invalid requests)
- Token limit exceeded
- Network errors
- File system errors (history storage)

## Examples

See the [examples](../examples/) directory for more detailed usage examples.
