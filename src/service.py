from nameko.rpc import rpc
from .chatbot import ChatbotService
from dotenv import load_dotenv

load_dotenv()


class RPCChatbot:
    name = "chatbot"

    @rpc
    def send_message(
        self, user_id: int, model: str, message: str, conversation_id: int = None
    ) -> str:
        return ChatbotService(user_id, model, conversation_id).send(message)
