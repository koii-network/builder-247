"""OpenRouter API client implementation."""

from typing import Optional
from .openai_client import OpenAIClient


class OpenRouterClient(OpenAIClient):
    """OpenRouter API client implementation using OpenAI's client."""

    def __init__(self, api_key: str, model: Optional[str] = None, **kwargs):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/koii-network",  # Required for OpenRouter
                "X-Title": "Koii Task Builder",  # Optional, but good practice
            },
            **kwargs,
        )

    def _get_api_name(self) -> str:
        """Get API name for logging."""
        return "OpenRouter"

    def _get_default_model(self) -> str:
        return "mistralai/mistral-small-3.1-24b-instruct:free"
