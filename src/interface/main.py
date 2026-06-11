import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_model import RequestEnvelope

from src.infrastructure.firestore_memory import FirestoreMemory
from src.infrastructure.groq_llm import GroqLLM
from src.application.assistant_service import AssistantService
from src.interface.alexa_handlers import (
    LaunchRequestHandler,
    ChatIntentHandler,
    YesIntentHandler,
    NoIntentHandler,
    HelpIntentHandler,
    GoodbyeIntentHandler,
    SessionEndedRequestHandler,
    FallbackIntentHandler,
)

memory = FirestoreMemory()
try:
    llm = GroqLLM()
except RuntimeError:
    llm = None

service = AssistantService(memory, llm)

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler(service))
sb.add_request_handler(ChatIntentHandler(service))
sb.add_request_handler(YesIntentHandler(service))
sb.add_request_handler(NoIntentHandler(service))
sb.add_request_handler(HelpIntentHandler(service))
sb.add_request_handler(GoodbyeIntentHandler(service))
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler(service))

serializer = DefaultSerializer()
skill = sb.create()

app = FastAPI(title="Aurora for Alexa")


@app.post("/")
async def alexa_endpoint(request: Request):
    body = json.dumps(await request.json())
    request_envelope = serializer.deserialize(body, RequestEnvelope)
    response_envelope = skill.invoke(request_envelope, {})
    return serializer.serialize(response_envelope)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug-groq")
async def debug_groq():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return {"error": "GROQ_API_KEY not set", "key_prefix": ""}
    try:
        from groq import Groq

        client = Groq(api_key=key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say hi"}],
            max_tokens=10,
            timeout=10,
        )
        return {
            "ok": True,
            "key_prefix": key[:8] + "...",
            "response": completion.choices[0].message.content.strip(),
        }
    except Exception as e:
        return {"error": str(e), "key_prefix": key[:8] + "..."}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
