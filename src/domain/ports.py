from abc import ABC, abstractmethod
from typing import Optional


class MemoryPort(ABC):
    @abstractmethod
    def get_history(self, user_id: str) -> list[dict]: ...

    @abstractmethod
    def save_exchange(self, user_id: str, role: str, content: str): ...

    @abstractmethod
    def get_profile(self, user_id: str) -> dict: ...

    @abstractmethod
    def save_profile(self, user_id: str, data: dict): ...


class LLMPort(ABC):
    @abstractmethod
    def ask(
        self, context: str, history: Optional[list[dict]] = None, user: str = ""
    ) -> str: ...

    @abstractmethod
    def extract_facts(self, text: str, user: str = "") -> list[str]: ...
