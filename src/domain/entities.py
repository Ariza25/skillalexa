from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Profile:
    name: Optional[str] = None
    facts: list[str] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)


@dataclass
class Conversation:
    user_id: str
    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))

    def last_turns(self, n: int = 20) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages[-n:]]
