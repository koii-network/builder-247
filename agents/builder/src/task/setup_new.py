# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from src.clients.anthropic_client_new import AnthropicClient
from pathlib import Path
from git import Repo


def setup_repository(repo_owner, repo_name, repo_path):
    """Configure repository with proper remotes without deleting directory"""
    repo_path = os.path.abspath(repo_path)
    print(f"Initializing repository at: {repo_path}")

    # Initialize repository
    repo = Repo.init(repo_path)

    # Configure remotes
    origin_url = f"https://github.com/{repo_owner}/{repo_name}.git"
    print(f"Setting origin remote to: {origin_url}")
    repo.create_remote("origin", origin_url)

    # Create initial commit if empty
    if not repo.heads:
        readme_path = os.path.join(repo_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {repo_name}\n\nInitial repository setup")
        repo.git.add(A=True)
        repo.git.commit(m="Initial commit")
        repo.git.branch("-M", "main")

    return repo_path


def setup_client() -> AnthropicClient:
    """Configure and return the Anthropic client with tools."""
    load_dotenv()

    client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])

    register_tools(client)

    return client


def register_tools(client: AnthropicClient):
    """Register tools using paths relative to container directory"""
    container_root = Path(__file__).parent.parent.parent  # Points to container/
    tool_dirs = [
        container_root / "src/tools/definitions/execute_command",
        container_root / "src/tools/definitions/file_operations",
        container_root / "src/tools/definitions/git_operations",
        container_root / "src/tools/definitions/github_operations",
    ]

    for tool_dir in tool_dirs:
        if not tool_dir.exists():
            raise FileNotFoundError(f"Tool directory not found: {tool_dir}")
        client.register_tools_from_directory(str(tool_dir))
