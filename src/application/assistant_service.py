import re
import locale
from datetime import datetime
from typing import Optional
from src.domain.ports import MemoryPort, LLMPort

_NAME_BLACKLIST = {
    "sim",
    "não",
    "nao",
    "oi",
    "olá",
    "ola",
    "tudo",
    "bem",
    "ok",
    "ah",
    "é",
}
_LOCALE_OK = False
for _loc in ("pt_BR.UTF-8", "Portuguese_Brazil.1252"):
    try:
        locale.setlocale(locale.LC_TIME, _loc)
        _LOCALE_OK = True
        break
    except locale.Error:
        continue
_DIAS_FALLBACK = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]
_MESES_FALLBACK = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


class AssistantService:
    def __init__(self, memory: MemoryPort, llm: Optional[LLMPort] = None):
        self._memory = memory
        self._llm = llm

    def has_name(self, user_id: str) -> bool:
        return bool(self._memory.get_profile(user_id).get("name"))

    def process_message(self, user_id: str, user_input: str) -> str:
        if not self._llm:
            return self._fallback()
        history = self._memory.get_history(user_id)
        profile = self._memory.get_profile(user_id)
        context = self._build_context(profile) + f"\n\nO usuário disse: '{user_input}'."
        try:
            response = self._llm.ask(context, history, user_id)
            if not response:
                return self._fallback()
            self._save_exchange(user_id, user_input, response)
            self._try_extract_name(user_id, user_input, response, profile)
            self._extract_facts(user_id, user_input)
            return response
        except Exception:
            return self._fallback()

    def _build_context(self, profile: dict) -> str:
        parts = []
        if profile.get("name"):
            parts.append(f"[Nome do usuário: {profile['name']}]")
        else:
            parts.append(
                "[Nome do usuário: desconhecido — descubra se parecer natural]"
            )
        if profile.get("facts"):
            parts.append(f"[Fatos conhecidos: {'; '.join(profile['facts'][-5:])}]")
        now = datetime.now()
        dia = now.strftime("%A") if _LOCALE_OK else _DIAS_FALLBACK[now.weekday()]
        mes = now.strftime("%B") if _LOCALE_OK else _MESES_FALLBACK[now.month - 1]
        parts.append(
            f"[Data/hora atual: {dia}, {now.day} de {mes} de {now.year}, {now.strftime('%H:%M')} BRT]"
        )
        return "\n".join(parts)

    def _save_exchange(self, user_id: str, user_input: str, response: str):
        self._memory.save_exchange(user_id, "user", user_input)
        self._memory.save_exchange(user_id, "assistant", response)

    def _try_extract_name(
        self, user_id: str, user_input: str, response: str, profile: dict
    ):
        if profile.get("name"):
            return
        patterns = [
            (r"(?:me\s+chamo|meu\s+nome\s+[eé])\s+(\w+)", None),
            (r"(?:sou\s+o|sou\s+a|sou)\s+(\w+)", None),
            (r"(?:pode\s+me\s+chamar\s+de)\s+(\w+)", None),
            (r"(?:me\s+chame\s+de)\s+(\w+)", None),
            (r"^(\w+)$", lambda n: len(n) >= 3 and n.lower() not in _NAME_BLACKLIST),
        ]
        for pat, validator in patterns:
            m = re.search(pat, user_input.strip(), re.IGNORECASE)
            if m:
                candidate = m.group(1).capitalize()
                if not validator or validator(candidate):
                    self._memory.save_profile(user_id, {"name": candidate})
                    break

    def _extract_facts(self, user_id: str, user_input: str):
        if not self._llm or len(user_input.strip()) < 5:
            return
        try:
            facts = self._llm.extract_facts(user_input, user_id)
            if facts:
                profile = self._memory.get_profile(user_id)
                existing = set(profile.get("facts", []))
                new = [f for f in facts if f not in existing]
                if new:
                    current = profile.get("facts", [])
                    self._memory.save_profile(user_id, {"facts": current + new})
        except Exception:
            pass

    @staticmethod
    def _fallback() -> str:
        import random

        return random.choice(
            [
                "Não entendi, senhor. Poderia repetir?",
                "Hmm, essa não estava nos meus planos. Pode reformular?",
                "Digamos que meu processador deu uma pausa. O que disse?",
            ]
        )
