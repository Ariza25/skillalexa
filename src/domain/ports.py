from abc import ABC, abstractmethod
from typing import Optional


class MemoryPort(ABC):
    @abstractmethod
    def get_history(self, user_id: str) -> list[dict]: ...

    @abstractmethod
    def save_exchange(self, user_id: str, role: str, content: str): ...


class LLMPort(ABC):
    @abstractmethod
    def ask(self, context: str, history: Optional[list[dict]] = None) -> str: ...
