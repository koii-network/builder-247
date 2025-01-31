# Tool Development Guidelines

This document outlines the standards and best practices for developing new tools in the Implementation Agent project.

## Tool Structure

Each tool should follow these core principles:

1. **Definition**: Define the tool interface in `src/tools/__init__.py` under `TOOL_DEFINITIONS` with:

   - Clear name following `snake_case` convention
   - Comprehensive description
   - Well-defined parameters with types and descriptions
   - Required vs optional parameters clearly marked

2. **Implementation**: Implement the tool in `src/tools/implementations.py`:
   - Extend the `ToolImplementations` class
   - Use type hints and docstrings
   - Return standardized `ToolResponse` objects
   - Handle errors with retry support

## Example Tool Definition

```python
{
    "name": "read_file",
    "description": "Read the contents of a file with security checks",
    "parameters": {
        "properties": {
            "relative_workspace_path": {
                "type": "string",
                "description": "Path to the file to read, relative to workspace root",
            },
            "should_read_entire_file": {
                "type": "boolean",
                "description": "Whether to read the entire file",
            },
            "start_line_one_indexed": {
                "type": "integer",
                "description": "The line to start reading from (1-indexed)",
            },
            "end_line_one_indexed_inclusive": {
                "type": "integer",
                "description": "The line to end reading at (1-indexed, inclusive)",
            }
        },
        "required": [
            "relative_workspace_path",
            "should_read_entire_file",
            "start_line_one_indexed",
            "end_line_one_indexed_inclusive"
        ],
    },
}
```

## Example Tool Implementation

```python
def read_file(
    self,
    relative_workspace_path: str,
    should_read_entire_file: bool,
    start_line_one_indexed: int,
    end_line_one_indexed_inclusive: int,
) -> ToolResponse:
    """Read a file with security checks.

    Args:
        relative_workspace_path: Path relative to workspace root
        should_read_entire_file: Whether to read entire file
        start_line_one_indexed: Start line (1-indexed)
        end_line_one_indexed_inclusive: End line (1-indexed)

    Returns:
        ToolResponse with file contents or error
    """
    try:
        # Use retry wrapper for error recovery
        @with_retry(config=self.retry_config)
        def read_operation():
            content = self.fs_tools.read_file(
                relative_workspace_path,
                should_read_entire_file,
                start_line_one_indexed,
                end_line_one_indexed_inclusive,
            )
            return ToolResponse(
                status=ToolResponseStatus.SUCCESS,
                data=content,
                metadata={
                    "path": relative_workspace_path,
                    "start_line": start_line_one_indexed,
                    "end_line": end_line_one_indexed_inclusive,
                },
            )

        return read_operation()

    except Exception as e:
        self.logger.log_error(
            "read_file",
            str(e),
            {
                "path": relative_workspace_path,
                "error_type": e.__class__.__name__,
            },
        )
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=f"Error reading file: {e}",
            metadata={"error_type": e.__class__.__name__},
        )
```

## Best Practices

1. **Security**

   - Always use SecurityContext for sensitive operations
   - Validate paths against workspace root
   - Sanitize command inputs and outputs
   - Handle environment variables securely

2. **Error Handling**

   - Use the retry mechanism for recoverable errors
   - Log errors with context using ToolLogger
   - Return structured error responses
   - Include detailed metadata

3. **Testing**

   - Write comprehensive unit tests
   - Test security constraints
   - Verify retry behavior
   - Test error handling paths

4. **Documentation**

   - Write clear docstrings
   - Document security considerations
   - Include retry behavior
   - Document metadata fields

5. **Performance**
   - Use appropriate timeouts
   - Handle large files efficiently
   - Consider memory constraints
   - Monitor resource usage

## Adding a New Tool

1. Define tool in `TOOL_DEFINITIONS`
2. Implement in `ToolImplementations`
3. Add security checks
4. Implement retry logic
5. Add comprehensive tests
6. Update documentation

## Common Patterns

1. **File Operations**

   - Use `FileSystemTools` with security checks
   - Validate paths against workspace
   - Handle line-based operations
   - Support partial file reads

2. **Command Execution**

   - Use `CommandExecutor` with security
   - Handle environment variables
   - Support piped commands
   - Sanitize output

3. **Response Format**
   ```python
   ToolResponse(
       status=ToolResponseStatus.SUCCESS,  # or ERROR
       data=result,                        # on success
       error=str(error),                   # on failure
       metadata={                          # always include metadata
           "path": "relative/path",
           "error_type": "ExceptionClass",
           "additional_context": "value",
       },
   )
   ```
