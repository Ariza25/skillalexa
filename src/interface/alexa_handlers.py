import random
from datetime import datetime
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from src.application.assistant_service import AssistantService

REPROMPTS = [
    "Algo mais, senhor?",
    "Mais alguma coisa?",
    "Em que mais posso ajudar?",
    "Deseja mais alguma coisa?",
    "Estou aqui. Precisa de algo?",
    "O que mais, senhor?",
]


def _ssml(text: str) -> str:
    return (
        f"<speak>"
        f'<voice name="Camila">'
        f'<prosody rate="medium">{text}</prosody>'
        f"</voice>"
        f"</speak>"
    )


def _respond(
    handler_input, service: AssistantService, prompt: str, should_ask: bool = True
):
    user_id = handler_input.request_envelope.context.system.user.user_id
    text = service.process_message(user_id, prompt)
    handler_input.response_builder.speak(_ssml(text))
    if should_ask:
        handler_input.response_builder.ask(random.choice(REPROMPTS))
    return handler_input.response_builder.response


class LaunchRequestHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        user_id = handler_input.request_envelope.context.system.user.user_id
        if self._service.has_name(user_id):
            prompt = f"{greeting}. O usuário acabou de te ativar. Cumprimente-o pelo nome com personalidade."
        else:
            prompt = f"{greeting}. O usuário acabou de te ativar. Pergunte quem está aí — você não sabe quem é."
        return _respond(handler_input, self._service, prompt)


class ChatIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        query = slots.get("query", None)
        user_text = query.value if query and query.value else "Continue a conversa."
        return _respond(
            handler_input,
            self._service,
            f"O usuário disse: '{user_text}'.",
        )


class YesIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "O usuário disse 'sim' para 'algo mais?'. Pergunte o que ele deseja.",
        )


class NoIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "O usuário está dispensando você. Despeça-se com seu estilo habitual.",
            should_ask=False,
        )


class HelpIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "O usuário está pedindo ajuda. Explique suas capacidades com seu estilo habitual.",
        )


class GoodbyeIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.StopIntent")(handler_input) or is_intent_name(
            "AMAZON.CancelIntent"
        )(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "O usuário está se despedindo. Despeça-se com estilo.",
            should_ask=False,
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    def __init__(self, service: AssistantService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "O usuário disse algo incompreensível. Peça para reformular com seu sarcasmo característico.",
        )
