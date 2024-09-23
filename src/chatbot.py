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
from langchain_core.chat_history import BaseChatMessageHistory
from . import orm
from operator import itemgetter

from langchain_core.runnables import RunnablePassthrough

MODELS = {
    "gpt-3.5-turbo": ChatOpenAI,
    "claude-3-5-sonnet-20240620": ChatAnthropic,
    "gemini-1.5-flash": ChatGoogleGenerativeAI,
    "gemini-1.5-pro": ChatGoogleGenerativeAI,
}


class History(BaseChatMessageHistory):
    messages: list[BaseMessage] = []
    conversation_id: int = None
    user_id: int = None

    def __init__(self, user_id: int, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def __persist_messages(self, messages: list[BaseMessage]):
        for message in messages or self.messages:
            orm.messages.create(
                data={
                    "conversation_id": self.conversation_id,
                    "content": message.content,
                    "type": message.type,
                }
            )

    def __load_conversation(self) -> dict:
        conversation = orm.conversations.get(
            by=["id", "user_id"],
            value=[self.conversation_id, self.user_id],
            joins=["messages"],
        ) or orm.conversations.create(
            data={"user_id": self.user_id},
            returns_object=True,
        )
        self.conversation_id = conversation["id"]
        return conversation

    def __set_messages(self, list_messages: list):
        self.messages = []
        for msg in list_messages:
            match msg.get("type"):
                case "human":
                    self.add_message(HumanMessage(content=msg.get("content")))
                case "ai":
                    self.add_message(AIMessage(content=msg.get("content")))
                case "system":
                    self.add_message(SystemMessage(content=msg.get("content")))
                case _:
                    raise ValueError(f"Unknown message type: {msg.get('type')}")

    def clear(self):
        self.messages = []
        self.conversation_id = None

    def add_message(self, message: BaseMessage):
        self.messages.append(message)
        self.__persist_messages([message])

    def retrieve(self) -> BaseChatMessageHistory:
        conversation = self.__load_conversation()
        self.__set_messages(conversation.get("messages", []))
        return self


class ChatbotService:
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content="You are a helpful assistant and a good joker"),
            MessagesPlaceholder(variable_name="conversation", optional=True),
            HumanMessage(content="{user_message}"),
        ]
    )
    trimmed: bool = True

    def __init__(
        self,
        user_id: int,
        conversation_id: int = None,
    ):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def get_history(self, user_id: int, conversation_id: int) -> Runnable:
        return History(user_id, conversation_id).retrieve()

    def model(self, model: str) -> Runnable:
        return MODELS[model](model=model)

    def __get_chain(self, model: str) -> Runnable:
        # TODO: add history to the chain
        if self.trimmed:
            trimmer = trim_messages(
                max_tokens=45,
                strategy="last",
                token_counter=self.model(model),
                # include_system=True,
                allow_partial=False,
                start_on="human",
            )
            chain = (
                RunnablePassthrough.assign(
                    messages=itemgetter("conversation") | trimmer
                )
                | self.prompt
                | self.model(model)
            )
        else:
            chain = self.prompt | self.model(model)

        get_session_history = lambda session_id: History(*session_id).retrieve()

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=get_session_history,
            input_messages_key="user_message",
            history_messages_key="conversation",
        )
        return chain_with_history

    def send(self, message: str, model: str) -> str:
        chain = self.__get_chain(model)
        ai_message: AIMessage = chain.invoke(
            {
                "user_message": message,
            },
            config={
                "session_id": (self.user_id, self.conversation_id),
            },
        )
        return ai_message.content

    def send_streamed(self, message: str, model: str):
        chain = self.__get_chain(model)
        ai_message_content: str = ""
        for chunk in chain.stream(
            {
                "user_message": message,
                "user_id": self.user_id,
                "conversation_id": self.conversation_id,
            }
        ):
            ai_message_content += chunk.content
            yield chunk.content, "ai", self.user_id, self.conversation["id"]
