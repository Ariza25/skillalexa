from typing import Optional
from src.domain.ports import MemoryPort, LLMPort


class JarvisService:
    def __init__(self, memory: MemoryPort, llm: Optional[LLMPort] = None):
        self._memory = memory
        self._llm = llm

    def process_message(self, user_id: str, user_input: str) -> str:
        if not self._llm:
            return self._fallback()
        history = self._memory.get_history(user_id)
        try:
            response = self._llm.ask(user_input, history)
            self._memory.save_exchange(user_id, "user", user_input)
            self._memory.save_exchange(user_id, "assistant", response)
            return response
        except Exception:
            return self._fallback()

    @staticmethod
    def _fallback() -> str:
        import random

        return random.choice(
            [
                "Não entendi, senhor. Poderia repetir?",
                "Senhor, essa solicitação não está nos meus parâmetros.",
                "Hum. Não encontro uma resposta para isso, senhor.",
            ]
        )
