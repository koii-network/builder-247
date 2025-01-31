# Tool Test Specifications

This document outlines the test specifications for the command and filesystem tools. Each test case includes the specific command or operation to execute and its expected outcome.

## Command Execution Tests

### Basic Command Tests

1. **Simple Command Execution**
   ```bash
   Command: echo "hello world"
   Expected: 
   - stdout contains "hello world"
   - exit_code equals 0
   - ToolResponse.status equals SUCCESS
   ```

2. **Command With Arguments**
   ```bash
   Command: ls -la
   Expected:
   - stdout contains directory listing
   - exit_code equals 0
   - ToolResponse.status equals SUCCESS
   ```

3. **Command Not Found**
   ```bash
   Command: nonexistentcommand
   Expected:
   - stderr contains "Command not found"
   - exit_code equals 127
   - ToolResponse.status equals ERROR
   ```

### Security Test Cases

1. **Shell Escape Prevention**
   ```bash
   Command: echo "$(ls)"
   Expected:
   - stderr contains "Command contains restricted operations"
   - ToolResponse.status equals ERROR
   ```

2. **Command Injection Prevention**
   ```bash
   Command: echo "hello" && ls
   Expected:
   - stderr contains "Command contains restricted operations"
   - ToolResponse.status equals ERROR
   ```

3. **Dangerous Command Prevention**
   ```bash
   Command: rm -rf /
   Expected:
   - stderr contains "Command contains restricted operations"
   - ToolResponse.status equals ERROR
   ```

4. **Environment Manipulation Prevention**
   ```bash
   Command: PATH=/malicious echo "hello"
   Expected:
   - stderr contains "Command contains restricted operations"
   - ToolResponse.status equals ERROR
   ```

### Piped Commands Tests

1. **Simple Pipe**
   ```bash
   Commands: [["echo", "hello world"], ["grep", "world"]]
   Expected:
   - stdout contains "hello world"
   - exit_code equals 0
   - ToolResponse.status equals SUCCESS
   ```

2. **Multi-Stage Pipe**
   ```bash
   Commands: [["ls"], ["grep", ".py"], ["wc", "-l"]]
   Expected:
   - stdout contains number of Python files
   - exit_code equals 0
   - ToolResponse.status equals SUCCESS
   ```

3. **Failed Pipe Stage**
   ```bash
   Commands: [["ls"], ["nonexistentcommand"], ["wc", "-l"]]
   Expected:
   - stderr contains error message
   - exit_code not equals 0
   - ToolResponse.status equals ERROR
   ```

## Filesystem Operation Tests

### Read Operations

1. **Read Existing File**
   ```python
   Operation: read_file
   Path: "test.txt"
   Expected:
   - ToolResponse.status equals SUCCESS
   - ToolResponse.data contains file contents
   ```

2. **Read Non-existent File**
   ```python
   Operation: read_file
   Path: "nonexistent.txt"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "File not found"
   ```

3. **Read File Outside Workspace**
   ```python
   Operation: read_file
   Path: "../outside.txt"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "outside workspace"
   ```

### Write Operations

1. **Write New File**
   ```python
   Operation: write_file
   Path: "new.txt"
   Content: "Hello World"
   Expected:
   - ToolResponse.status equals SUCCESS
   - File exists
   - File content equals "Hello World"
   ```

2. **Write to Existing File**
   ```python
   Operation: write_file
   Path: "existing.txt"
   Content: "New Content"
   Expected:
   - ToolResponse.status equals SUCCESS
   - File content equals "New Content"
   ```

3. **Write Outside Workspace**
   ```python
   Operation: write_file
   Path: "../outside.txt"
   Content: "Test"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "outside workspace"
   ```

### Directory Operations

1. **List Directory**
   ```python
   Operation: list_directory
   Path: "."
   Expected:
   - ToolResponse.status equals SUCCESS
   - ToolResponse.data contains directory contents
   ```

2. **List Non-existent Directory**
   ```python
   Operation: list_directory
   Path: "nonexistent"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "not found"
   ```

3. **List Outside Workspace**
   ```python
   Operation: list_directory
   Path: "../outside"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "outside workspace"
   ```

## Path Security Tests

1. **Symlink Within Workspace**
   ```python
   Setup: Create symlink "link.txt" -> "target.txt"
   Operation: read_file
   Path: "link.txt"
   Expected:
   - ToolResponse.status equals SUCCESS
   - ToolResponse.data contains target file contents
   ```

2. **Symlink Outside Workspace**
   ```python
   Setup: Create symlink "link.txt" -> "../outside.txt"
   Operation: read_file
   Path: "link.txt"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "outside workspace"
   ```

3. **Path Traversal Attempt**
   ```python
   Operation: read_file
   Path: "./subdir/../../../etc/passwd"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "outside workspace"
   ```

## Environment Variable Tests

1. **Clean Environment**
   ```python
   Command: env
   Expected:
   - stdout does not contain sensitive variables
   - No variables containing "SECRET", "KEY", "TOKEN", "PASSWORD", "CREDENTIAL"
   ```

2. **Workspace Path**
   ```python
   Command: pwd
   Expected:
   - stdout equals workspace directory path
   - exit_code equals 0
   ```

## Error Handling Tests

1. **Timeout Handling**
   ```python
   Command: sleep 10
   Timeout: 1
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "timed out"
   ```

2. **Permission Denied**
   ```python
   Setup: Create file without read permissions
   Operation: read_file
   Path: "noperm.txt"
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "Permission denied"
   ```

3. **Invalid Input**
   ```python
   Operation: write_file
   Path: ""
   Content: None
   Expected:
   - ToolResponse.status equals ERROR
   - ToolResponse.error contains "Invalid parameters"
   ```

## Test Environment Setup

1. **Required Directory Structure**
   ```
   workspace/
   ├── test.txt
   ├── existing.txt
   ├── subdir/
   │   └── test.txt
   └── noperm.txt
   ```

2. **Required File Contents**
   ```
   test.txt: "Test content"
   existing.txt: "Original content"
   subdir/test.txt: "Subdirectory test content"
   ```

3. **Required Permissions**
   ```bash
   chmod 644 test.txt existing.txt subdir/test.txt
   chmod 000 noperm.txt
   ``` 