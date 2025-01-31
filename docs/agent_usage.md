# Using the Implementation Agent

The Implementation Agent is an AI-powered tool that helps automate the implementation of todo items in your codebase. It uses Claude 3 Opus to analyze requirements, plan changes, implement code, and verify the implementation through tests.

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The agent is configured using the `AgentConfig` class with the following parameters:

Required:

- `workspace_dir` (Path): Directory containing your codebase

Optional:

- `model` (str): Claude model to use, defaults to "claude-3-opus-20240229"
- `max_retries` (int): Maximum retry attempts for failing operations, defaults to 3
- `log_file` (str): Path to log file for agent operations
- `api_key` (str): Anthropic API key (will use ANTHROPIC_API_KEY env var if not provided)
- `max_tokens` (int): Maximum tokens in conversation window, defaults to 100000
- `history_dir` (Path): Directory for storing conversation history
- `allowed_paths` (List[Path]): List of paths that can be accessed, defaults to workspace_dir
- `allowed_env_vars` (List[str]): List of environment variables that can be accessed
- `restricted_commands` (List[str]): List of commands that are not allowed

Example configuration:

```python
from pathlib import Path
from src.agent import AgentConfig, ImplementationAgent

config = AgentConfig(
    workspace_dir=Path("./my_project"),
    model="claude-3-opus-20240229",
    max_retries=3,
    log_file="agent.log",
    max_tokens=100000,
    history_dir=Path("./history"),
    allowed_paths=[Path("./my_project"), Path("/tmp")],
    allowed_env_vars=["PATH", "HOME", "USER"],
    restricted_commands=["rm -rf", "sudo", ">", "dd"]
)
agent = ImplementationAgent(config)
```

## Components

The agent uses several key components:

1. **AnthropicClient**: Handles communication with the Claude API

   - Manages conversation history and token limits
   - Supports conversation persistence
   - Handles tool calls and responses

2. **CommandExecutor**: Safely executes shell commands with security checks

   - Enforces command security policies
   - Handles environment variables safely
   - Supports piped commands

3. **SecurityContext**: Manages security constraints and protected resources

   - Controls allowed paths and commands
   - Protects sensitive environment variables
   - Sanitizes command output

4. **ToolLogger**: Provides structured logging of operations
   - Logs operations and errors
   - Supports file-based logging
   - Includes operation context

## Usage

### Implementing Todo Items

To implement a todo item, use the `implement_todo()` method with a description and list of acceptance criteria:

```python
todo_item = "Add logging to authentication module"
acceptance_criteria = [
    "Use structured logging format",
    "Include timestamp, severity, and request ID in logs",
    "Log all authentication attempts"
]

success = agent.implement_todo(todo_item, acceptance_criteria)
if success:
    print("Implementation successful!")
else:
    print("Implementation failed - check logs for details")
```

The agent will:

1. Analyze the requirements
2. Plan the implementation
3. Make necessary code changes
4. Generate and run tests
5. Iterate on failing tests up to max_retries times

### Conversation History

The agent now supports persistent conversation history:

```python
# Configure with history directory
config = AgentConfig(
    workspace_dir=Path("./my_project"),
    history_dir=Path("./history")
)
agent = ImplementationAgent(config)

# History is automatically saved during interactions
```

The conversation history includes:

- User messages
- Assistant responses
- Timestamps
- Token counts

### Security

The agent enforces security through multiple layers:

1. **Command Execution**:

   - Restricted command patterns
   - Protected environment variables
   - Safe working directory handling

2. **File Operations**:

   - Path validation
   - Permission checks
   - Workspace directory restrictions

3. **Environment Protection**:
   - Sensitive variable filtering
   - Output sanitization
   - Resource constraints

### Monitoring Progress

The agent logs all operations to the configured log file (if specified) or to the default Python logger. The logs include:

- Operation start/end times
- Implementation plans
- Test results
- Error details
- Tool execution results

### Error Handling

The agent handles various error conditions:

- Network/API errors when communicating with Claude
- Test failures with automatic retries
- File system permission issues
- Command execution errors
- Token limit exceeded errors

Errors are logged and propagated appropriately to the calling code.

## Best Practices

1. **Clear Requirements**: Provide detailed, specific acceptance criteria
2. **Test Coverage**: Ensure your project has good test coverage
3. **Version Control**: Run the agent in a clean git branch
4. **Review Changes**: Always review the agent's changes before committing
5. **Logging**: Configure a log file to track the agent's operations
6. **Security**: Review the security context configuration for your environment
7. **History Management**: Use history_dir for persistent conversations
8. **Token Management**: Monitor and adjust max_tokens based on your needs

## Example Workflow

```python
from pathlib import Path
from src.agent import AgentConfig, ImplementationAgent

# Configure the agent
config = AgentConfig(
    workspace_dir=Path("./my_project"),
    log_file="agent.log",
    history_dir=Path("./history"),
    max_tokens=100000
)
agent = ImplementationAgent(config)

# Define todo item
todo = "Add rate limiting to API endpoints"
criteria = [
    "Implement token bucket algorithm",
    "Rate limit should be configurable per endpoint",
    "Return 429 status when limit exceeded",
    "Include rate limit headers in responses"
]

# Run implementation
if agent.implement_todo(todo, criteria):
    print("Rate limiting implemented successfully!")
else:
    print("Implementation failed - check agent.log for details")
```

## Troubleshooting

Common issues and solutions:

1. **Tests Failing**: Check test output and agent logs for details
2. **Permission Errors**: Ensure proper file permissions in workspace
3. **API Errors**: Verify API key and network connectivity
4. **Memory Issues**: Reduce model context size or break down larger tasks
5. **Security Restrictions**: Review security context if operations are blocked
6. **Token Limits**: Adjust max_tokens if conversations are too long
7. **History Issues**: Check history_dir permissions and space

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.
