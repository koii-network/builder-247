# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
import tempfile
from pathlib import Path
from src.anthropic_client import AnthropicClient
from src.tools.github_operations import check_fork_exists, fork_repository, sync_fork
from src.tools.git_operations import create_branch, checkout_branch, list_branches
from src.tools.file_operations import read_file, write_file, move_file, copy_file, rename_file, delete_file, list_files
import shutil
from anthropic.types import (
    ToolParam,
    ToolChoiceParam,
    ContentBlockParam,
    ToolUseBlock,
    Message,
    TextBlock,
)

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
        
    def create_feature_branch(self, repo_path: str, branch_name: str = "feature"):
        """Create and switch to a new branch"""
        create_result = create_branch(repo_path, branch_name)
        if not create_result["success"]:
            raise Exception(f"Failed to create branch: {create_result['error']}")
            
        checkout_result = checkout_branch(repo_path, branch_name)
        if not checkout_result["success"]:
            raise Exception(f"Failed to checkout branch: {checkout_result['error']}")
            
    def get_file_list(self, repo_path: str):
        """Get the list of files in the repository"""
        return list(Path(repo_path).rglob("*"))
    




def setup_environment():
    """Set environment variables"""
    load_dotenv()
    api_key = os.environ.get("CLAUDE_API_KEY")

    return AnthropicClient(api_key=api_key)

if __name__ == "__main__":
    temp_path = "./test"
    client = setup_environment()
    
    # Initialize the flow
    from_repo = "https://github.com/HermanKoii/dummyExpress.git"
    example_todo = "Add a CoinGekko API; Create a Test for the API to make it work; Add error handling."
    
    flow = GitHubFlow(from_repo, example_todo, temp_path)
    
    try:
        # Set up the repository
        repo_path = flow.setup_repository()
        # Create a feature branch
        flow.create_feature_branch(repo_path)
        
        # Get the list of files
        files = flow.get_file_list(repo_path)
        print(files)
        client = setup_environment()

        client.register_tools_from_directory("./src/tools/definitions/execute_command")
        client.register_tools_from_directory("./src/tools/definitions/file_operations")
        client.register_tools_from_directory("./src/tools/definitions/git_operations")
        client.register_tools_from_directory("./src/tools/definitions/github_operations")
        additional_info = 'Here is the list of files in the repo' + str(files) 
        # Start interaction with Claude
        print ("start")
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
            if not isinstance(tool_output, str):
                tool_output = str(tool_output)
            
            response = client.send_message(tool_output or "Operation Finished")
            max_iterations -= 1
        
        print ("end")
        # TODO: Implement interaction with Claude to complete the task

        # 2. Design the solution
        # 3. Write tests
        # 4. Implement the feature
        # 5. Run tests and fix issues
        # 6. Sync branches and handle conflicts
        # 7. Create PR
        
    except Exception as e:
        print(f"Error: {str(e)}")

    
    