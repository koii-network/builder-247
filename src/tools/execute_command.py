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

        stdout, stderr = [], []

        # Read stdout and stderr line by line
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Print stdout in real-time
            stdout.append(line)

        for line in iter(process.stderr.readline, ''):
            print(line, end='')  # Print stderr in real-time
            stderr.append(line)

        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()

        # Return the output, error, and return code
        return ''.join(stdout), ''.join(stderr), return_code
    except subprocess.TimeoutExpired:
        return "", "operation too long, over 5 minutes", -1  
    except Exception as e:
        return "", str(e), -1
