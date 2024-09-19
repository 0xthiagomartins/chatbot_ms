from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
from langchain_core.runnables import Runnable

MODELS = {
    "gpt-3.5-turbo": ChatOpenAI,
    "claude-3-5-sonnet-20240620": ChatAnthropic,
    "gemini-1.5-flash": ChatVertexAI,
}


class ChatbotService:
    def __init__(self, user_id: int, model: str):
        self.runnable = self.__get_runnable(model)
        self.user_id = user_id

    def __get_runnable(self, model: str) -> Runnable:
        return MODELS[model](model=model)

    def send_message(self, message: str):
        return self.runnable.invoke(message)

    def get_chat_history(self):
        return self.runnable.get_chat_history(self.user_id)

    def get_chat_history_messages(self):
        return self.runnable.get_chat_history_messages(self.user_id)
