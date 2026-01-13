from abc import ABC, abstractmethod
from typing import Dict, Iterable, List


class LLMProvider(ABC):
    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]]) -> Iterable[str]:
        raise NotImplementedError
