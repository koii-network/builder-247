import sys
from pathlib import Path
import dotenv
from datetime import datetime
from anthropic.types import ToolUseBlock
import os

# Conditional path adjustment before any other imports
if __name__ == "__main__":
    # Calculate path to project root
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from src.task.setup import setup_client

dotenv.load_dotenv()

PROMPTS = {
    "convert_file": (
        "Read the following JSONL file and create a new CSV file with two columns: 'todo' and "
        "'acceptance_criteria'.\n"
        "The todo should contain:\n"
        "- The core problem description\n"
        "- Required function signatures and parameters\n"
        "- Input/output specifications and data formats\n"
        "Do not include:\n"
        "- Sample code or solutions\n"
        "- Step-by-step explanations\n"
        "- Optional hints or tips\n\n"
        "The acceptance criteria should start with 'All tests must pass.' and include:\n"
        "- All constraints and requirements from the problem\n"
        "- Input/output requirements\n"
        "- Performance requirements\n"
        "- Special conditions that must be handled\n\n"
        "Save the output file in the same directory as the input file, with the same name but with a "
        ".csv extension.\n\n"
        "Example of a line in the input JSONL file:\n"
        '{{"response": "Here is a coding challenge that involves finding and deleting duplicate '
        "elements in an array. Given an array arr[] of size n containing only integers, write a function named "
        "deleteDuplicates that deletes all the duplicate elements in the array, but maintains the order of the "
        "elements. The function should return the modified array. Note: The function should not use any built-in "
        'functions or libraries to remove duplicates."}}'
        "\n\n"
        "Example output row in CSV:\n"
        '"Given an array of size N containing only integers, write a function that deletes all the '
        'duplicate elements in the array while maintaining the order of the elements.","All tests must pass. '
        "The function should return the modified array. The function should not use any built-in functions or "
        'libraries to remove duplicates."'
        "\n\n"
        "Input file: {input_file}\n"
    ),
    "system_prompt": (
        "You are an expert data processor. Your task is to convert JSONL files containing coding challenges to CSV "
        "files. For each challenge:\n\n"
        "ESSENTIAL - You must preserve:\n"
        "1. Problem specifications (e.g., grid formats, data structures, valid values)\n"
        "2. Input/output formats and requirements\n"
        "3. Constraints and limitations\n"
        "4. Every challenge from the original file must be present in the output\n"
        "DO NOT include:\n"
        "1. Line breaks in the todo or acceptance criteria\n"
        "2. Sample inputs/outputs used to demonstrate the problem\n"
        "3. Code snippets or solution approaches\n"
        "4. Explanatory notes or tips\n"
        "5. Additional constraints not stated in the problem\n\n"
        "Remember: If removing something would make the problem impossible to implement correctly, it must be kept."
    ),
}


def handle_tool_response(client, response):
    """
    Handle tool responses until natural completion.
    """
    print("Start Conversation")

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            print(f"Processing tool: {tool_use.name}")
            print(f"Tool input: {tool_use.input}")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Execute the tool
            tool_output = client.execute_tool(tool_use)
            print(f"Tool output: {tool_output}")

            # Send tool result back to AI
            response = client.send_message(
                tool_response=str(tool_output),
                tool_use_id=tool_use.id,
                conversation_id=response.conversation_id,
            )

    print("End Conversation")


def process_files(input_dir):
    """
    Process all JSONL files in the input directory and create corresponding CSV files.
    """
    # Set up client
    client = setup_client()

    # Change to input directory so agent can use relative paths
    original_dir = os.getcwd()
    os.chdir(input_dir)

    try:
        # Get all JSONL files in the directory
        jsonl_files = list(Path().glob("*.jsonl"))

        for input_file in jsonl_files:
            file_name = input_file.name
            print(f"\nProcessing {file_name}")

            # Create new conversation for each file
            conversation_id = client.create_conversation(
                system_prompt=PROMPTS["system_prompt"],
            )

            # Send conversion prompt
            convert_prompt = PROMPTS["convert_file"].format(input_file=file_name)
            print("Sending prompt:", convert_prompt)

            response = client.send_message(
                prompt=convert_prompt, conversation_id=conversation_id
            )

            # Handle tool responses
            handle_tool_response(client, response)

            print(f"Completed processing {file_name}")
    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    # Get the data directory path
    data_dir = Path(__file__).parent.parent.parent.parent.parent / "data" / "process"

    # Process all JSONL files in the directory
    process_files(data_dir)
