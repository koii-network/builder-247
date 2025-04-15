import subprocess
import os
from prometheus_swarm.types import ToolOutput


def execute_command(command: str, **kwargs) -> ToolOutput:
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
            timeout=300,  # Add a 5-minute timeout to prevent hanging
        )

        # For command execution, success means the command was executed without exceptions
        # The return code is provided separately and can be interpreted by the caller
        message = result.stdout if result.stdout else result.stderr
        message = message or "Command executed with no output"

        return {
            "success": True,  # Command executed without exceptions
            "message": message,
            "data": {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command_succeeded": result.returncode
                == 0,  # Separate flag for command's own success
            },
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "message": f"Command timed out after 300 seconds: {str(e)}",
            "data": {
                "stdout": e.stdout if hasattr(e, "stdout") and e.stdout else "",
                "stderr": e.stderr if hasattr(e, "stderr") and e.stderr else "",
                "returncode": -1,
                "timed_out": True,
                "command_succeeded": False,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to execute command: {str(e)}",
            "data": {
                "error": str(e),
                "command_succeeded": False,
            },
        }


def run_tests(
    path: str, framework: str, **kwargs  # Default but can be overridden
) -> ToolOutput:
    """Run tests using the specified framework and command.

    If no command provided, uses project defaults based on framework:
    - pytest: "pytest {path}"
    - jest: "jest {path}"
    - vitest: "npx vitest {path}"
    etc.
    """

    commands = {
        "pytest": f"python3 -m pytest {path if path else ''} -v",
        "jest": f"jest {path if path else ''}",
        "vitest": f"npx vitest {path if path else ''} --run",  # Add --run flag to ensure it doesn't start in watch mode
    }
    command = commands.get(framework)
    if not command:
        return {
            "success": False,
            "message": f"Unknown test framework: {framework}",
            "data": None,
        }

    result = execute_command(command)

    # Check if the command execution failed (not the tests)
    if not result["success"]:
        return {
            "success": False,
            "message": f"Failed to execute tests: {result['message']}",
            "data": result.get("data", {}),
        }

    # Check if the command timed out
    if result.get("data", {}).get("timed_out"):
        return {
            "success": False,
            "message": "Tests timed out. This may be due to tests running in watch mode or waiting for user input.",
            "data": {
                "output": result.get("message", ""),
                "returncode": -1,
                "tests_passed": False,
                "timed_out": True,
            },
        }

    # Combine stdout and stderr for complete test output
    output = []
    if result["data"]["stdout"]:
        output.append(result["data"]["stdout"])
    if result["data"]["stderr"]:
        output.append(result["data"]["stderr"])

    output_str = "\n".join(output) if output else "No test output captured"

    # For test frameworks, a non-zero return code usually means tests failed, not that the command failed
    tests_passed = result["data"]["returncode"] == 0

    # Determine message based on test results
    message = (
        "Tests completed successfully."
        if tests_passed
        else "Tests completed with failures."
    )
    message += " See output for details."

    # For tests, success means the command ran successfully
    # The actual test results are in the output
    return {
        "success": True,  # True if we got test results, even if tests failed
        "message": message,
        "data": {
            "output": output_str,
            "returncode": result["data"]["returncode"],
            "tests_passed": tests_passed,
            "framework": framework,
        },
    }


def install_dependency(
    package_name: str,
    package_manager: str,
    is_dev_dependency: bool = False,
    version: str = None,
    **kwargs,
) -> ToolOutput:
    """Install a dependency using the specified package manager.

    Supports common package managers with appropriate flags to prevent hanging:
    - npm: Uses --no-fund --no-audit flags
    - pip: Uses --no-cache-dir flag
    - yarn: Uses --non-interactive flag
    - pnpm: Uses --no-fund flag

    Args:
        package_name: Name of the package to install
        package_manager: Package manager to use (npm, pip, yarn, pnpm)
        is_dev_dependency: Whether to install as a dev dependency (where applicable)
        version: Specific version to install (optional)
    """
    package_spec = package_name
    if version:
        if package_manager in ["npm", "yarn", "pnpm"]:
            package_spec = f"{package_name}@{version}"
        elif package_manager == "pip":
            package_spec = f"{package_name}=={version}"

    commands = {
        "npm": {
            "prod": f"npm install --no-fund --no-audit {package_spec}",
            "dev": f"npm install --no-fund --no-audit --save-dev {package_spec}",
        },
        "pip": {
            "prod": f"pip install --no-cache-dir {package_spec}",
            "dev": f"pip install --no-cache-dir {package_spec}",  # pip doesn't have dev dependencies
        },
        "yarn": {
            "prod": f"yarn add --non-interactive {package_spec}",
            "dev": f"yarn add --non-interactive --dev {package_spec}",
        },
        "pnpm": {
            "prod": f"pnpm add --no-fund {package_spec}",
            "dev": f"pnpm add --no-fund --save-dev {package_spec}",
        },
    }

    if package_manager not in commands:
        return {
            "success": False,
            "message": f"Unsupported package manager: {package_manager}",
            "data": None,
        }

    dep_type = "dev" if is_dev_dependency else "prod"
    command = commands[package_manager][dep_type]

    result = execute_command(command)

    # Check if the command execution failed
    if not result["success"]:
        return {
            "success": False,
            "message": f"Failed to install dependency: {result['message']}",
            "data": result.get("data", {}),
        }

    # For package managers, a non-zero return code usually means the installation failed
    installation_succeeded = result["data"]["command_succeeded"]

    # Add context to the result
    result_data = {
        "package_name": package_name,
        "package_manager": package_manager,
        "is_dev_dependency": is_dev_dependency,
        "installation_succeeded": installation_succeeded,
        "stdout": result["data"]["stdout"],
        "stderr": result["data"]["stderr"],
        "returncode": result["data"]["returncode"],
    }

    if version:
        result_data["version"] = version

    # Determine message based on installation results
    if installation_succeeded:
        message = f"Successfully installed {package_spec} using {package_manager}"
    else:
        message = f"Failed to install {package_spec} using {package_manager}. See output for details."

    return {
        "success": True,  # Command executed without exceptions
        "message": message,
        "data": result_data,
    }


def setup_dependencies(
    package_manager: str, repo_path: str = None, **kwargs
) -> ToolOutput:
    """Install dependencies from requirements.txt or package.json.

    Args:
        repo_path: Path to the repository root. If None, uses current directory.

    Returns:
        ToolOutput: Standardized tool output with installation status
    """
    try:
        working_dir = repo_path or os.getcwd()
        print(f"Installing dependencies in {working_dir}")

        if package_manager == "pip":
            requirements_path = os.path.join(working_dir, "requirements.txt")
            if not os.path.exists(requirements_path):
                return {
                    "success": False,
                    "message": "Requirements.txt not found",
                    "data": None,
                }

            result = execute_command(
                f"pip install --no-cache-dir -r {requirements_path}"
            )
        elif package_manager == "npm":
            package_json_path = os.path.join(working_dir, "package.json")
            if not os.path.exists(package_json_path):
                return {
                    "success": False,
                    "message": "package.json not found",
                    "data": None,
                }
            result = execute_command(
                f"npm install --no-fund --no-audit -r {requirements_path}"
            )
        elif package_manager == "yarn":
            package_json_path = os.path.join(working_dir, "package.json")
            if not os.path.exists(package_json_path):
                return {
                    "success": False,
                    "message": "package.json not found",
                    "data": None,
                }
            result = execute_command(
                f"yarn add --non-interactive -r {requirements_path}"
            )
        elif package_manager == "pnpm":
            package_json_path = os.path.join(working_dir, "package.json")
            if not os.path.exists(package_json_path):
                return {
                    "success": False,
                    "message": "package.json not found",
                    "data": None,
                }
            result = execute_command(f"pnpm add --no-fund -r {requirements_path}")

        success = result["data"]["command_succeeded"]
        stdout = result["data"]["stdout"]
        stderr = result["data"]["stderr"]
        returncode = result["data"]["returncode"]

        if success:
            message = "Dependencies installed successfully"
        else:
            message = "Failed to install dependencies"

        return {
            "success": True,  # Tool executed without exceptions
            "message": message,
            "data": {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
            },
        }

    except Exception as e:
        error_msg = f"Error installing dependencies: {str(e)}"
        print(error_msg)
        return {"success": False, "message": error_msg, "data": None}
