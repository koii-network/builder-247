"""x.ai API client implementation."""

from typing import Optional
from .openai_client import OpenAIClient


class XAIClient(OpenAIClient):
    """x.ai API client implementation using OpenAI's client."""

    def __init__(self, api_key: str, model: Optional[str] = None, **kwargs):
        super().__init__(
            api_key=api_key, model=model, base_url="https://api.x.ai/v1", **kwargs
        )

    def _get_api_name(self) -> str:
        """Get API name for logging."""
        return "x.ai"

    def _get_default_model(self) -> str:
        return "grok-2-latest"
