from nameko.rpc import rpc
from .chatbot import ChatbotService


class ChatService:
    def __init__(self):
        self.chatbot = ChatbotService()

    @rpc
    def send_message(self, user_id, message):
        return self.chatbot.process_message(user_id, message)
