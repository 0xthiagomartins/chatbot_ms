from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import Runnable
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    trim_messages,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from . import orm

MODELS = {
    "gpt-3.5-turbo": ChatOpenAI,
    "claude-3-5-sonnet-20240620": ChatAnthropic,
    "gemini-1.5-flash": ChatGoogleGenerativeAI,
    "gemini-1.5-pro": ChatGoogleGenerativeAI,
}


class ChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, messages: list = []):
        self.messages: list[BaseMessage] = messages
        for msg in messages:
            match msg.get("type"):
                case "human":
                    self.messages.append(HumanMessage(content=msg.get("content")))
                case "ai":
                    self.messages.append(AIMessage(content=msg.get("content")))
                case "system":
                    self.messages.append(SystemMessage(content=msg.get("content")))
                case _:
                    raise ValueError(f"Unknown message type: {msg.get('type')}")

    def clear(self):
        self.messages = []

    def add_message(self, message: BaseMessage):
        self.messages.append(message)


class ChatbotService:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content="You are a helpful assistant and a good joker"),
            MessagesPlaceholder(variable_name="conversation", optional=True),
            HumanMessage(content="{user_message}"),
        ]
    )

    def __init__(
        self,
        user_id: int,
        model: str,
        conversation_id: int = None,
        trimmed: bool = False,
    ):
        self.trimmed = trimmed
        self.model = self.__get_model(model)
        self.parser = StrOutputParser()
        self.user_id = user_id
        self.conversation: dict = self.__get_conversation(conversation_id)
        self.history: BaseChatMessageHistory = ChatMessageHistory(
            self.conversation.get("messages", [])
        )

    def __get_model(self, model: str) -> Runnable:
        return MODELS[model](model=model)

    def __get_conversation(self, conversation_id: int = None):
        conversation = orm.conversations.get(
            by=["id", "user_id"],
            value=[conversation_id, self.user_id],
            joins=["messages"],
        ) or orm.conversations.create(
            data={"user_id": self.user_id},
            returns_object=True,
        )
        conversation["messages"] = conversation.get("messages", [])
        return conversation

    def __get_chain(self):
        if self.trimmed:
            trimmer = trim_messages(
                max_tokens=45,
                strategy="last",
                token_counter=self.model,
                include_system=True,
            )
            return trimmer | self.prompt | self.model
        return self.prompt | self.model

    def send(self, message: str) -> str:
        chain = self.__get_chain()
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=lambda: self.history,
            input_messages_key="user_message",
            history_messages_key="conversation",
        )
        self.__save_message(HumanMessage(content=message))
        ai_message: AIMessage = chain_with_history.invoke({"user_message": message})
        self.__save_message(ai_message)
        return ai_message.content

    def __save_message(self, lc_message: BaseMessage):
        data = {
            "conversation_id": self.conversation["id"],
            "content": lc_message.content,
            "type": lc_message.type,
        }
        orm.messages.create(data=data)
        self.conversation["messages"].append(data)
