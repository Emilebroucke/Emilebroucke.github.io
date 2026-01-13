import json
from typing import Dict, Iterable, List

import httpx

from ..config import settings
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model or "gemini-1.5-pro"
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.base_url = settings.llm_base_url or "https://generativelanguage.googleapis.com"

    def stream_chat(self, messages: List[Dict[str, str]]) -> Iterable[str]:
        contents = []
        for message in messages:
            role = "user" if message["role"] != "assistant" else "model"
            contents.append({"role": role, "parts": [{"text": message["content"]}]})
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            },
        }
        url = (
            f"{self.base_url.rstrip('/')}/v1beta/models/{self.model}:streamGenerateContent"
        )
        with httpx.stream("POST", url, params={"key": self.api_key}, json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[len("data: ") :]
                else:
                    data = line
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                for candidate in payload.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        text = part.get("text")
                        if text:
                            yield text
