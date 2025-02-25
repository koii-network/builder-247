from src.tools.execute_command.implementations import execute_command, run_tests


DEFINITIONS = {
    "execute_command": {
        "name": "execute_command",
        "description": "Execute a shell command in the current working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute",
                }
            },
            "required": ["command"],
        },
        "function": execute_command,
    },
    "run_tests": {
        "name": "run_tests",
        "description": "Run tests using a specified framework.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to test file or directory.",
                },
                "framework": {
                    "type": "string",
                    "description": "Test framework to use.",
                    "enum": ["pytest", "jest"],
                },
            },
            "required": ["framework", "path"],
        },
        "function": run_tests,
    },
}
