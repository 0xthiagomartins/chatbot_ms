from nameko.rpc import rpc
from .chatbot import ChatbotService
from dotenv import load_dotenv

load_dotenv()


class RPCChatbot:
    name = "chatbot"

    @rpc
    def send_message(self, user_id, model: str, message: str):
        return ChatbotService(user_id, model).send(message)
