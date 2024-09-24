from typing import Any
from nameko.rpc import rpc
from nameko.events import event_handler, EventDispatcher
from .chatbot import ChatbotService
from . import orm
from dotenv import load_dotenv

load_dotenv()


class RPCChatbot:
    name = "chatbot"

    dispatch = EventDispatcher()
    session: dict = {
        "user_id": 1,
        "conversation_id": 63,
    }
    received_messages = []

    @rpc
    def list_conversations(self) -> list[dict]:
        return orm.conversations.list(
            filter={"user_id": self.user_id, "archived": False},
            mode="all",
            order={"updated_at": "desc"},
        )

    @rpc
    def get_conversation(self, conversation_id: int) -> dict:
        return orm.conversations.get(
            by=["id", "user_id", "archived"],
            value=[self.user_id, conversation_id, False],
        )

    @rpc
    def send(self, model: str, message: str, stream: bool = False) -> str:
        if stream:
            for chunk in ChatbotService(
                self.user_id, self.conversation_id
            ).send_streamed(message, model):
                self.dispatch("stream_event", chunk)
        else:
            return ChatbotService(self.user_id, self.conversation_id).send(
                message, model
            )

    #### STREAM QUEUE ####

    @event_handler("chatbot", "stream_event")
    def handle_stream_event(self, payload):
        print(f"Received Event: {payload}")

    @rpc
    def get_received_messages(self):
        return self.received_messages
