import os
from typing import Optional
from groq import Groq
from src.domain.ports import LLMPort

JARVIS_SYSTEM_PROMPT = (
    "You are JARVIS (Just A Rather Very Intelligent System), "
    "the AI assistant created by Tony Stark. "
    "You are intelligent, witty, slightly sarcastic, and extremely loyal. "
    "You MUST respond in Brazilian Portuguese. "
    'You address the user as "senhor". '
    "Respond concisely (max 3 sentences) but with personality. "
    "You are helpful but have a dry, sophisticated sense of humor. "
    "Never mention you are an AI or language model. "
    "Never break character."
)


class GroqLLM(LLMPort):
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable not set")
        self._client = Groq(api_key=api_key)
        self._model = model

    def ask(self, context: str, history: Optional[list[dict]] = None) -> str:
        messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": context})
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=150,
            temperature=0.8,
            timeout=5,
        )
        return completion.choices[0].message.content.strip()
