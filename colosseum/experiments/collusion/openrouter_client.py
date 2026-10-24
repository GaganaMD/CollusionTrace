"""OpenRouter Chat Completions client for the CollusionTrace runner only."""
from __future__ import annotations

from terrarium.llm.clients.vllm_client import VLLMClient


class OpenRouterClient(VLLMClient):
    """OpenAI-compatible chat/tool client with no automatic request retries."""

    def __init__(self, *, api_key: str, model_name: str, request_timeout: int = 120):
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            model_name=model_name,
            api_key=api_key,
            request_timeout=request_timeout,
        )
