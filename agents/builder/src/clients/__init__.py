# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from pathlib import Path
from src.clients.anthropic_client import AnthropicClient
from src.clients.xai_client import XAIClient
from src.clients.openai_client import OpenAIClient
from src.clients.base_client import Client


def setup_client(client: str, tools_dir: str = None) -> Client:
    """Configure and return the an LLM client with tools.

    Args:
        client: The client type to use ("openai", "anthropic", or "xai")
        tools_dir: Optional path to tools directory. If not provided, will use default location
    """
    load_dotenv()

    client_config = clients[client]
    client = client_config["client"](api_key=os.environ[client_config["api_key"]])

    # If no tools_dir provided, calculate it relative to project root
    if tools_dir is None:
        # Get the project root (3 levels up from this file)
        project_root = Path(__file__).resolve().parent.parent.parent
        tools_dir = str(project_root / "src" / "tools")
    else:
        # Convert provided path to absolute path
        tools_dir = str(Path(tools_dir).resolve())

    client.register_tools(tools_dir)
    return client


clients = {
    "anthropic": {"client": AnthropicClient, "api_key": "ANTHROPIC_API_KEY"},
    "xai": {"client": XAIClient, "api_key": "XAI_API_KEY"},
    "openai": {"client": OpenAIClient, "api_key": "OPENAI_API_KEY"},
}
