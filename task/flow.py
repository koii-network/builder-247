from task.setup import setup_repository, setup_client
import os
from anthropic.types import (
    ToolUseBlock,
)
from src.get_file_list import get_file_list
from src.tools.git_operations import get_current_branch
from task.constants import PROMPTS


def handle_tool_response(client, response, tool_choice={"type": "any"}, max_iterations=10):
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
        print ("tool_output for first 50 characters: " + str(tool_output)[:50])
        
        # Ensure tool_output is a string
        if not isinstance(tool_output, str):
            tool_output = str(tool_output)
        
        response = client.send_message(tool_response=tool_output, tool_use_id=tool_use.id, conversation_id=response.conversation_id, tool_choice=tool_choice)
        max_iterations -= 1
    print("End Conversation")
def todo_to_pr(repo_owner="HermanKoii", repo_name="dummyExpress", repo_path = "./test", todo = "Add a /grassprice API to fetch https://api.coingecko.com/api/v3/simple/price?ids=<coin_name>&vs_currencies=usd; Create a Test for the API to make it work; Add error handling."):
    """
    Task flow
    """

    # print("Using Directory:", os.getcwd())
    # print("Using path:", repo_path)
    client = setup_client()
    # print("Client: ", client)
    try:
        # Set up the repository
        repo_path = setup_repository(repo_owner, repo_name, repo_path)
        print("Setup repository result: ", repo_path)
        # Create a feature branch
        setup_repository_prompt = PROMPTS["setup_repository"].format(repo_path=repo_path, todo=todo)
        print("Setup repository prompt: ", setup_repository_prompt)
        createBranchResponse = client.send_message(setup_repository_prompt)
        print("Create branch response: ", createBranchResponse)
        handle_tool_response(client, createBranchResponse)
        print("Create branch response: ", createBranchResponse)
        branch_info = get_current_branch(repo_path)
        
        branch_name = branch_info.get("output") if branch_info.get("success") else None
        print("Using Branch: ", branch_name)
        # Get the list of files
        files = get_file_list(repo_path)
        print("Use Files: ", files)
        files_directory = PROMPTS["files"].format(files=', '.join(map(str, files)))
        execute_todo_response = client.send_message(todo + files_directory)
        handle_tool_response(client, execute_todo_response)
        github_username = os.environ.get("GITHUB_USERNAME")
        commit_response = client.send_message(PROMPTS["commit"].format(
            repo_path=repo_path,
            todo=todo
        ), tool_choice={"type": "any"})
        handle_tool_response(client, commit_response, tool_choice={"type": "tool", "name": "make_commit"})
        push_response = client.send_message(PROMPTS["push"].format(
            repo_path=repo_path
        ), tool_choice={"type": "tool", "name": "push_remote"})
        handle_tool_response(client, push_response, tool_choice={"type": "tool", "name": "push_remote"})
        create_pr_response = client.send_message(PROMPTS["create_pr"].format(
            repo_path=repo_path,
            todo=todo, 
            repo_full_name=f"{repo_owner}/{repo_name}", 
            head=f"{github_username}:{branch_name}", 
            base="master"
        ), tool_choice={"type": "any"})
        handle_tool_response(client, create_pr_response, tool_choice={"type": "tool", "name": "create_pull_request"})
        
    except Exception as e:
        print(f"Error: {str(e)}")
if __name__ == "__main__":
    # read from ./todo.txt, and each line you need to run todo_to_pr
    with open("./todo.txt", "r") as f:
        for line in f:
            todo = line.strip()
            # print("Todo: ", todo)
            todo_to_pr(todo=todo)
    # todo_to_pr()
    
    