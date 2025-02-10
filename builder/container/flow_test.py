# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
import tempfile
from pathlib import Path
from src.anthropic_client import AnthropicClient
from src.tools.github_operations import check_fork_exists, fork_repository, sync_fork, create_pull_request
from src.tools.git_operations import create_branch, checkout_branch, make_commit, push_remote, get_current_branch
from src.tools.file_operations import read_file, write_file, move_file, copy_file, rename_file, delete_file, list_files
import shutil
from anthropic.types import (
    ToolUseBlock,
)
from src.get_file_list import get_file_list
class GitHubFlow:
    def __init__(self, from_repo: str, todo: str, workspace_dir: str):
        self.from_repo = from_repo
        self.todo = todo
        self.workspace_dir = workspace_dir
        self.repo_owner, self.repo_name = from_repo.split("/")[-2:]
        self.repo_name = self.repo_name.replace(".git", "")
        
    def setup_repository(self):
        """Check if the branch exists, sync or create the branch"""
        # Check if the branch exists
        fork_check = check_fork_exists(self.repo_owner, self.repo_name)
        
        repo_path = self.workspace_dir
        
        if fork_check["success"] and fork_check["exists"]:
            # If the branch exists, ensure the path exists
            if not os.path.exists(repo_path):
                # If the path does not exist, clone the repository first
                fork_result = fork_repository(f"{self.repo_owner}/{self.repo_name}", self.workspace_dir)
                if not fork_result["success"]:
                    raise Exception(f"Failed to create fork: {fork_result['error']}")
                
            # Sync it
            sync_result = sync_fork(repo_path, "master")
            if not sync_result["success"]:
                raise Exception(f"Failed to sync fork: {sync_result['error']}")
        else:
            # If the branch does not exist, create it
            # Check and delete existing directory before cloning
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            fork_result = fork_repository(f"{self.repo_owner}/{self.repo_name}", self.workspace_dir)
            if not fork_result["success"]:
                raise Exception(f"Failed to create fork: {fork_result['error']}")
            
            # Add debug information
            if not os.path.exists(repo_path):
                raise Exception(f"Cloning failed, path does not exist: {repo_path}")
            
        return repo_path
        
    # def create_feature_branch(self, repo_path: str, branch_name: str = "feature"):
    #     """Create and switch to a new branch"""
    #     create_result = create_branch(repo_path, branch_name)
    #     if not create_result["success"]:
    #         raise Exception(f"Failed to create branch: {create_result['error']}")
            
    #     checkout_result = checkout_branch(repo_path, branch_name)
    #     if not checkout_result["success"]:
    #         raise Exception(f"Failed to checkout branch: {checkout_result['error']}")
            

    




def setup_environment():
    """Set environment variables"""
    load_dotenv()
    api_key = os.environ.get("CLAUDE_API_KEY")

    return AnthropicClient(api_key=api_key)

if __name__ == "__main__":
    ############## Debugging current local repository ###############
    print("Current working directory:", os.getcwd())

    # Debugging the path
    temp_path = "./test"
    print("Using path:", temp_path)

    # # Ensure the directory exists
    # if not os.path.exists(temp_path):
    #     os.makedirs(temp_path)

    # # Write operation
    # try:
    #     with open(os.path.join(temp_path, "test_file.txt"), "w") as f:
    #         f.write("Test content")
    #     print("File written successfully.")
    # except Exception as e:
    #     print(f"Error writing file: {e}")
    # ############### Debugging current local repository ###############

    client = setup_environment()
    client.register_tools_from_directory("./src/tools/definitions/execute_command")
    client.register_tools_from_directory("./src/tools/definitions/file_operations")
    client.register_tools_from_directory("./src/tools/definitions/git_operations")
    client.register_tools_from_directory("./src/tools/definitions/github_operations")
    # Initialize the flow
    from_repo = "https://github.com/HermanKoii/dummyExpress.git"
    example_todo = "Add a /arweaveprice API to fetch https://api.coingecko.com/api/v3/simple/price?ids=<coin_name>&vs_currencies=usd; Create a Test for the API to make it work; Add error handling."
    
    flow = GitHubFlow(from_repo, example_todo, temp_path)
    
    try:
        # Set up the repository
        repo_path = flow.setup_repository()
        # Create a feature branch
        response = client.send_message("Create or checkout to the branch for repo path './test' only, do not execute the todos:" + example_todo)
        max_iterations = 10
        while response.stop_reason == "tool_use" and max_iterations > 0:
            tool_use = [block for block in response.content if block.type == "tool_use"][0]
            tool_name = tool_use.name
            tool_input = tool_use.input
            print ("tool_name: " + tool_name)
            print ("tool_input: " + str(tool_input))
            tool_output = client.execute_tool(ToolUseBlock(id=tool_use.id, name=tool_name, input=tool_input, type='tool_use'))
            # print ("tool_output: " + str(tool_output))
            
            # Ensure tool_output is a string
            if not isinstance(tool_output, str):
                tool_output = str(tool_output)
            
            response = client.send_message(tool_response=tool_output, tool_use_id=tool_use.id, conversation_id=response.conversation_id)
            max_iterations -= 1
        print("finished iteration")
        # Get the list of files
        files = get_file_list(repo_path)
        # print(files)
        branch_info = get_current_branch(repo_path)
        branch_name = branch_info.get("output") if branch_info.get("success") else None
        print("Current Branch name", branch_name)
        # client.register_tools_from_directory("./src/tools/definitions/git_operations")
        # client.register_tools_from_directory("./src/tools/definitions/github_operations")
        additional_info = 'Here is the list of files in the repo: ' + ', '.join(map(str, files)) + "Please use cd test to enter the repo path."

        print ("Start conversation")
        response = client.send_message(example_todo + additional_info)
        print ("response: " + str(response))

        
        max_iterations = 10
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
        
        print ("end")
        
        # print(response.content)

        check_out_branch_result = create_branch(repo_path, branch_name)
        print ("check_out_branch_result: " + str(check_out_branch_result))

        make_commit_result = make_commit(repo_path, "all files", True)
        print ("make_commit_result: " + str(make_commit_result))

        push_result = push_remote(repo_path, "origin")
        print ("push_result: " + str(push_result))
        
        # make a pr
        SampleDescription = """
            ### Type of Change
            - [x] New feature
            - [ ] Bug fix
            - [ ] Documentation update
            - [ ] Code refactoring
            - [ ] Other

            ### Description
            This pull request introduces a new feature that enhances the existing functionality by integrating a CoinGekko API. The feature allows users to fetch real-time cryptocurrency data, which is crucial for the application's financial analysis module. Additionally, error handling mechanisms have been implemented to ensure robustness.

            ### Related Issues
            - None

            ### Testing Done
            Manual testing was conducted to ensure the new feature works as expected. The API integration was tested with various endpoints, and error handling was verified under different failure scenarios.

            ### Checklist
            - [x] I have tested my changes
            - [x] I have performed a self-review of my own code
            - [x] I have commented my code, particularly in hard-to-understand areas
            - [x] I have made corresponding changes to the documentation
            - [x] My changes generate no new warnings
            - [x] I have added tests that prove my fix is effective or that my feature works
            - [x] New and existing unit tests pass locally with my changes
            - [x] I confirm that testing has been completed
        """
        response = client.send_message("Create a description for the below to do request" + example_todo + "in the following format: "+ SampleDescription)
        real_description = response.content[0].text
        print("text",real_description)
        create_pr_result = create_pull_request(repo_full_name="HermanKoii/dummyExpress", title="feature", body=SampleDescription, head=f"HermanL02:{branch_name}", base="master")
        ################################# AUTO PR NOT WORKING DUE TO RATE LIMIT #########################
        # print ("create a commit please")
        # response = client.send_message("Help me to use the tools commit and push"+additional_info)
        # print ("response: " + str(response))
        # max_iterations = 10
        # while response.stop_reason == "tool_use" and max_iterations > 0:
        #     tool_use = [block for block in response.content if block.type == "tool_use"][0]
        #     tool_name = tool_use.name
        #     tool_input = tool_use.input
        #     print ("tool_name: " + tool_name)
        #     print ("tool_input: " + str(tool_input))
        #     tool_output = client.execute_tool(ToolUseBlock(id=tool_use.id, name=tool_name, input=tool_input, type='tool_use'))
        #     print ("tool_output: " + str(tool_output))
        #     if not isinstance(tool_output, str):
        #         tool_output = str(tool_output)
        #     response = client.send_message(tool_response=tool_output,tool_use_id=tool_use.id, conversation_id=response.conversation_id)
        #     max_iterations -= 1
        # print ("end")
        ############ AUTO PR NOT WORKING DUE TO RATE LIMIT #########################
    except Exception as e:
        print(f"Error: {str(e)}")

    
    