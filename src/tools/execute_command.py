import subprocess


def execute_command(command):
    """
    Execute an arbitrary command line command.

    Parameters:
    command (str): The command to execute.

    Returns:
    tuple: A tuple containing the output, error message, and return code.
    """
    try:
        # Execute the command
        if not command.strip():  # Check if the command is empty or just whitespace
            return (
                "",
                "command not found",
                1,
            )  # Return an error message and a non-zero return code

        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        # Return the output, error, and return code
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1
