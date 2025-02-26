import subprocess
import os
from src.types import ToolOutput


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
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": None,
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
        }

    result = execute_command(command)

    # Combine stdout and stderr for complete test output
    output = []
    if result["data"]["stdout"]:
        output.append(result["data"]["stdout"])
    if result["data"]["stderr"]:
        output.append(result["data"]["stderr"])

    output_str = "\n".join(output) if output else "No test output captured"

    # Return success=True only if tests passed (returncode=0)
    # But always include the test output in the message
    return {
        "success": result["data"]["returncode"] == 0,
        "message": output_str,
        "data": {"output": output_str, "returncode": result["data"]["returncode"]},
    }
