from task.setup import setup_repository, setup_client
import os
from anthropic.types import (
    ToolUseBlock,
)
from src.get_file_list import get_file_list
from src.tools.git_operations import create_branch, checkout_branch, make_commit, push_remote, get_current_branch
from task.constants import PROMPTS


def handle_tool_response(client, response, max_iterations=10):
    """
    Handle tool responses recursively until we get a text response.
    """
    print("Start Conversation")
    while response.stop_reason == "tool_use" and max_iterations > 0:
        tool_use = [block for block in response.content if block.type == "tool_use"][0]
        tool_name = tool_use.name
        tool_input = tool_use.input
        print ("tool_name: " + tool_name)
        print ("tool_input: " + str(tool_input))
        tool_output = client.execute_tool(ToolUseBlock(id=tool_use.id, name=tool_name, input=tool_input, type='tool_use'))
        print ("tool_output: " + str(tool_output))
        
        # Ensure tool_output is a string
        if not isinstance(tool_output, str):
            tool_output = str(tool_output)
        
        response = client.send_message(tool_response=tool_output, tool_use_id=tool_use.id, conversation_id=response.conversation_id)
        max_iterations -= 1
    print("End Conversation")
def task(repo_owner="HermanKoii", repo_name="dummyExpress", repo_path = "./test", todo = "Add a /grassprice API to fetch https://api.coingecko.com/api/v3/simple/price?ids=<coin_name>&vs_currencies=usd; Create a Test for the API to make it work; Add error handling."):
    """
    Task flow
    """

    print("Using Directory:", os.getcwd())
    print("Using path:", repo_path)
    client = setup_client()
    try:
        # Set up the repository
        repo_path = setup_repository(repo_owner, repo_name, repo_path)
        # Create a feature branch
        createBranchResponse = client.send_message(PROMPTS["setup_repository"].format(repo_path=repo_path, todo=todo))
        handle_tool_response(client, createBranchResponse)
    
        branch_info = get_current_branch(repo_path)
        branch_name = branch_info.get("output") if branch_info.get("success") else None
        print("Using Branch: ", branch_name)
        # Get the list of files
        files = get_file_list(repo_path)
        files_directory = PROMPTS["files"].format(files=', '.join(map(str, files)))
        execute_todo_response = client.send_message(todo + files_directory)
        handle_tool_response(client, execute_todo_response)
        github_username = os.environ.get("GITHUB_USERNAME")

        commit_push_create_pr_response = client.send_message(PROMPTS["commit_push_create_pr"].format(
            repo_path=repo_path,
            todo=todo, 
            repo_full_name=f"{repo_owner}/{repo_name}", 
            head=f"{github_username}:{branch_name}", 
            base="master"
        ))
        handle_tool_response(client, commit_push_create_pr_response)
    except Exception as e:
        print(f"Error: {str(e)}")
if __name__ == "__main__":
    task()
    
    
    