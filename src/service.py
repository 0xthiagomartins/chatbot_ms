from nameko.rpc import rpc
from nameko.events import event_handler, EventDispatcher
import json
from .chatbot import ChatbotService
from . import orm
from dotenv import load_dotenv

load_dotenv()


class RPCChatbot:
    name = "chatbot"

    dispatch = EventDispatcher()
    received_messages = []

    @rpc
    def list_conversations(self, user_id: int) -> list[dict]:
        return orm.conversations.list(
            filter={"user_id": user_id, "archived": False},
            mode="all",
            order={"updated_at": "desc"},
        )

    @rpc
    def get_conversation(self, user_id: int, conversation_id: int) -> dict:
        return orm.conversations.get(
            by=["id", "user_id", "archived"], value=[conversation_id, user_id, False]
        )

    @rpc
    def send_message(
        self, user_id: int, model: str, message: str, conversation_id: int = None
    ) -> str:
        return ChatbotService(user_id, model, conversation_id).send(message)

    @rpc
    def send_streamed_message(
        self, user_id: int, model: str, message: str, conversation_id: int = None
    ):
        for chunk in ChatbotService(user_id, model, conversation_id).send_streamed(
            message
        ):
            self.dispatch("stream_event", chunk)

    #### STREAM QUEUE ####

    @event_handler("chatbot", "stream_event")
    def handle_stream_event(self, payload):
        print(f"Received Event: {payload}")

    @rpc
    def get_received_messages(self):
        return self.received_messages
