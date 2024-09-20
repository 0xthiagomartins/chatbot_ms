from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
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
from . import orm

MODELS = {
    "gpt-3.5-turbo": ChatOpenAI,
    "claude-3-5-sonnet-20240620": ChatAnthropic,
    "gemini-1.5-flash": ChatVertexAI,
}
SYSTEM_MESSAGE: BaseMessage = SystemMessage(content="You are a helpful assistant.")


class ChatbotService:
    prompt = ChatPromptTemplate.from_messages(
        [
            SYSTEM_MESSAGE,
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content="{question}"),
        ]
    )

    def __init__(self, user_id: int, model: str, conversation_id: int = None):
        self.model = self.__get_model(model)
        self.parser = StrOutputParser()
        self.user_id = user_id
        self.conversation = self.__get_conversation(conversation_id)

    def __get_model(self, model: str) -> Runnable:
        return MODELS[model](model=model)

    def __get_conversation(self, conversation_id: int = None):
        conversation = orm.Conversation.get(
            by=["id", "user_id"],
            value=[conversation_id, self.user_id],
            join=["messages"],
        ) or orm.Conversation.create(
            data={"user_id": self.user_id},
            returns_object=True,
        )
        return conversation

    def get_messages(self) -> list[BaseMessage]:
        messages: list[dict[str, str]] = self.conversation.get("messages", [])
        parsed_messages: list[BaseMessage] = []
        for msg in messages:
            match msg.get("role"):
                case "user":
                    parsed_messages.append(HumanMessage(content=msg.get("content")))
                case "ai":
                    parsed_messages.append(AIMessage(content=msg.get("content")))
                case _:
                    raise ValueError(f"Unknown message type: {msg.get('role')}")

        return parsed_messages

    def send_message(self, message: str, trimmed: bool = True):
        if trimmed:
            trimmer = trim_messages(
                max_tokens=45,
                strategy="last",
                token_counter=self.model,
                include_system=True,
            )
            chain = trimmer | self.prompt | self.model | self.parser
        else:
            chain = self.prompt | self.model | self.parser
        chain_with_history = RunnableWithMessageHistory(
            chain,
            self.get_messages,
            input_messages_key="question",
            history_messages_key="history",
        )
        return chain_with_history.invoke([HumanMessage(content=message)])
