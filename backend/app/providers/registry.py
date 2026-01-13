from ..config import settings
from .anthropic import AnthropicProvider
from .base import LLMProvider
from .gemini import GeminiProvider
from .openai_compat import OpenAICompatibleProvider


def get_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider in {"openai", "openai-compatible", "local"}:
        return OpenAICompatibleProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    if provider == "gemini":
        return GeminiProvider()
    return OpenAICompatibleProvider()
