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
SYSTEM_MESSAGE: BaseMessage = SystemMessage(content="You are a helpful assistant.")


class ChatMessageHistory(BaseChatMessageHistory):
    def __init__(self):
        self.messages = []

    def clear(self):
        self.messages = []


class ChatbotService:
    prompt = ChatPromptTemplate.from_messages(
        [
            SYSTEM_MESSAGE,
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content="{question}"),
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
        self.conversation = self.__get_conversation(conversation_id)

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

    def get_messages(self) -> BaseChatMessageHistory:
        messages: list[dict[str, str]] = self.conversation.get("messages", [])
        history = ChatMessageHistory()
        for msg in messages:
            match msg.get("role"):
                case "human":
                    history.messages.append(HumanMessage(content=msg.get("content")))
                case "ai":
                    history.messages.append(AIMessage(content=msg.get("content")))
                case _:
                    raise ValueError(f"Unknown message type: {msg.get('role')}")

        return history

    def send(self, message: str):
        chain = self.__get_chain()
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=self.get_messages,
            input_messages_key="question",
            history_messages_key="history",
        )
        ai_message: AIMessage = chain_with_history.invoke({"question": message})
        orm.messages.create(
            data={
                "conversation_id": self.conversation["id"],
                "content": ai_message.content,
                "is_from_user": False,
            }
        )
        return ai_message.content
