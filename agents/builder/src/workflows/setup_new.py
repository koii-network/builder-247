# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from src.clients.anthropic_client_new import AnthropicClient
from src.clients.xai_client import XAIClient
from src.clients.openai_client import OpenAIClient
from pathlib import Path
from git import Repo
from src.clients.base_client import Client


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


def setup_client(client: str) -> Client:
    """Configure and return the an LLM client with tools."""
    load_dotenv()

    client = clients[client](api_key=os.environ[api_keys[client]])

    register_tools(client)

    return client


def register_tools(client: Client):
    """Register tools using paths relative to container directory"""
    container_root = Path(__file__).parent.parent.parent  # Points to container/
    tool_dirs = [
        container_root / "src/tools/execute_command",
        container_root / "src/tools/file_operations",
        container_root / "src/tools/git_operations",
        container_root / "src/tools/github_operations",
    ]

    for tool_dir in tool_dirs:
        if not tool_dir.exists():
            raise FileNotFoundError(f"Tool directory not found: {tool_dir}")
        client.register_tools(str(tool_dir))


clients = {
    "anthropic": AnthropicClient,
    "xai": XAIClient,
    "openai": OpenAIClient,
}

api_keys = {
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
    "openai": "OPENAI_API_KEY",
}
