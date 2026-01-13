import json
from typing import Dict, Iterable, List

import httpx

from ..config import settings
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model or "claude-3-5-sonnet-20240620"
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        self.base_url = settings.llm_base_url or "https://api.anthropic.com"

    def stream_chat(self, messages: List[Dict[str, str]]) -> Iterable[str]:
        system = ""
        user_messages = []
        for message in messages:
            if message["role"] == "system":
                system += f"{message['content']}\n"
            else:
                user_messages.append(message)
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system.strip(),
            "messages": user_messages,
            "stream": True,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        with httpx.stream(
            "POST",
            f"{self.base_url.rstrip('/')}/v1/messages",
            headers=headers,
            json=payload,
            timeout=60.0,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[len("data: ") :]
                else:
                    data = line
                if data.strip() == "[DONE]":
                    break
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if payload.get("type") == "content_block_delta":
                    delta = payload.get("delta", {})
                    text = delta.get("text")
                    if text:
                        yield text
