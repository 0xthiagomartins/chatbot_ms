from nameko.rpc import rpc
from .chatbot import ChatbotService
from . import orm
from dotenv import load_dotenv

load_dotenv()


class RPCChatbot:
    name = "chatbot"

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
