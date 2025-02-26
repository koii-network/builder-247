import subprocess
import os
from src.clients.types import ToolOutput


def execute_command(command: str) -> ToolOutput:
    """Execute a shell command in the current working directory."""
    try:
        cwd = os.getcwd()
        print(f"Executing command in {cwd}: {command}")

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        message = result.stdout if result.returncode == 0 else result.stderr
        message = message or "Command failed with no error output"
        return {
            "success": result.returncode == 0,  # Only success if return code is 0
            "message": message,
            "data": {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
            "error": result.stderr if result.returncode != 0 else None,
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to execute command",
            "data": None,
            "error": str(e),
        }


def run_tests(
    path: str,
    framework: str,  # Default but can be overridden
) -> ToolOutput:
    """Run tests using the specified framework and command.

    If no command provided, uses project defaults based on framework:
    - pytest: "pytest {path}"
    - jest: "jest {path}"
    etc.
    """

    commands = {
        "pytest": f"python3 -m pytest {path if path else ''} -v",
        "jest": f"jest {path if path else ''}",
    }
    command = commands.get(framework)
    if not command:
        return {
            "success": False,
            "message": f"Unknown test framework: {framework}",
            "data": None,
            "error": f"Unknown test framework: {framework}",
        }

    result = execute_command(command)

    if not result["success"]:
        error_msg = []
        if result.get("stdout"):
            error_msg.append("Test output:\n" + result["stdout"])
        if result.get("stderr"):
            error_msg.append("Error output:\n" + result["stderr"])
        error = "\n".join(error_msg) if error_msg else "Tests failed with no output"
        return {
            "success": False,
            "message": "Tests failed",
            "data": result["data"],
            "error": error,
        }

    return {
        "success": True,
        "message": "Tests completed successfully",
        "data": result["data"],
        "error": None,
    }
