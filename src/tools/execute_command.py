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

        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired:
       
            process.kill()
       
            stdout, stderr = process.communicate()
       
            process.__exit__(None, None, None)
            return stdout, "Command timed out after 5 minutes", -1

        # Return the output, error, and return code
        return stdout, stderr, process.returncode
    except Exception as e:
        return "", str(e), -1
