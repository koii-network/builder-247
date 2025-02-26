# check if a fork exists, sync if it does, create a fork if it doesn't
from dotenv import load_dotenv
import os
from agents.builder.src.clients.anthropic_client import AnthropicClient
from src.clients.xai_client import XAIClient
from src.clients.openai_client import OpenAIClient
from src.clients.base_client import Client


def setup_client(client: str) -> Client:
    """Configure and return the an LLM client with tools."""
    load_dotenv()

    client_config = clients[client]

    client = client_config["client"](api_key=os.environ[client_config["api_key"]])

    client.register_tools("src/tools/")

    return client


clients = {
    "anthropic": {"client": AnthropicClient, "api_key": "ANTHROPIC_API_KEY"},
    "xai": {"client": XAIClient, "api_key": "XAI_API_KEY"},
    "openai": {"client": OpenAIClient, "api_key": "OPENAI_API_KEY"},
}
