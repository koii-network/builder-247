"""LocalAI client implementation using OpenAI's client."""

from typing import Optional
from .openai_client import OpenAIClient


class LocalAIClient(OpenAIClient):
    """LocalAI client implementation using OpenAI's client."""

    def __init__(
        self,
        api_key: str = "not-needed",
        model: Optional[str] = None,
        base_url: str = "http://localhost:8080/v1",
        **kwargs
    ):
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    def _get_api_name(self) -> str:
        """Get API name for logging."""
        return "LocalAI"

    def _get_default_model(self) -> str:
        return "gpt-3.5-turbo"  # Or whatever model you have configured
