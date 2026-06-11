from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from src.application.jarvis_service import JarvisService


def _ssml(text: str) -> str:
    return f'<speak><prosody rate="medium" pitch="low">{text}</prosody></speak>'


def _respond(
    handler_input, service: JarvisService, prompt: str, should_ask: bool = True
):
    user_id = handler_input.request_envelope.context.system.user.user_id
    text = service.process_message(user_id, prompt)
    handler_input.response_builder.speak(_ssml(text))
    if should_ask:
        handler_input.response_builder.ask("Algo mais, senhor?")
    return handler_input.response_builder.response


class LaunchRequestHandler(AbstractRequestHandler):
    def __init__(self, service: JarvisService):
        self._service = service

    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "The user just activated you. Greet them warmly.",
        )


class ChatIntentHandler(AbstractRequestHandler):
    def __init__(self, service: JarvisService):
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
            f"The user said: '{user_text}'. Respond as JARVIS in character.",
        )


class HelpIntentHandler(AbstractRequestHandler):
    def __init__(self, service: JarvisService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "The user is asking for help. Offer your capabilities.",
        )


class GoodbyeIntentHandler(AbstractRequestHandler):
    def __init__(self, service: JarvisService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.StopIntent")(handler_input) or is_intent_name(
            "AMAZON.CancelIntent"
        )(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "The user is saying goodbye. Bid them farewell.",
            should_ask=False,
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    def __init__(self, service: JarvisService):
        self._service = service

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        return _respond(
            handler_input,
            self._service,
            "The user said something unintelligible. Ask them to rephrase.",
        )
