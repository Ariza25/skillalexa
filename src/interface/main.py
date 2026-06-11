import os
import json
from fastapi import FastAPI, Request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_model import RequestEnvelope

from src.infrastructure.firestore_memory import FirestoreMemory
from src.infrastructure.groq_llm import GroqLLM
from src.application.jarvis_service import JarvisService
from src.interface.alexa_handlers import (
    LaunchRequestHandler,
    ChatIntentHandler,
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

service = JarvisService(memory, llm)

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler(service))
sb.add_request_handler(ChatIntentHandler(service))
sb.add_request_handler(HelpIntentHandler(service))
sb.add_request_handler(GoodbyeIntentHandler(service))
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler(service))

serializer = DefaultSerializer()
skill = sb.create()

app = FastAPI(title="Jarvis for Alexa")


@app.post("/")
async def alexa_endpoint(request: Request):
    body = json.dumps(await request.json())
    request_envelope = serializer.deserialize(body, RequestEnvelope)
    response_envelope = skill.invoke(request_envelope, {})
    return serializer.serialize(response_envelope)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
