import subprocess
import os


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
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
