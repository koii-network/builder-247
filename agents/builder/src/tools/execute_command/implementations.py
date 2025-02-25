import subprocess
import os
from typing import Dict, Any


def execute_command(command: str) -> dict:
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
        return {
            "success": result.returncode == 0,  # Only success if return code is 0
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_tests(
    path: str,
    framework: str,  # Default but can be overridden
) -> Dict[str, Any]:
    """Run tests using the specified framework and command.

    If no command provided, uses project defaults based on framework:
    - pytest: "pytest {path}"
    - jest: "jest {path}"
    etc.
    """

    commands = {
        "pytest": f"python3 -m pytest {path if path else ''}",
        "jest": f"jest {path if path else ''}",
    }
    command = commands.get(framework)
    if not command:
        return {"success": False, "error": f"Unknown test framework: {framework}"}

    return execute_command(command)
