from sqlmodel import Relationship, Field as F
from sqlmodel_controller import BaseID
from datetime import datetime
import secrets


class User(BaseID, table=True):
    __tablename__ = "users"

    username: str = F(None, unique=True, index=True)
    email: str = F(None, unique=True, index=True)
    hashed_password: str = F(None)
    full_name: str = F("")
    is_active: bool = F(True)
    salt: str = F(default_factory=lambda: secrets.token_hex(16))
    default_text_model: str = F("gpt-3.5-turbo")
    default_image_model: str = F("dall-e-3")
    theme: str = F("dark")
    language: str = F("en")
    show_options_menu_when_clicking_a_message: bool = F(False)
    show_explicit_content: bool = F(False)
    storage_used: int = F(0)
    storage_limit: int = F(1000000000)  # unit: bytes

    conversations: list["Conversation"] = Relationship(back_populates="user")


class Conversation(BaseID, table=True):
    __tablename__ = "conversations"

    user_id: int = F(foreign_key="users.id")
    title: str = F("New Conversation")

    messages: list["ConversationMessage"] = Relationship(back_populates="conversation")
    user: User = Relationship(back_populates="conversations")


class ConversationMessage(BaseID, table=True):
    __tablename__ = "conversation_messages"

    conversation_id: int = F(foreign_key="conversations.id")
    content: str
    timestamp: datetime = F(default_factory=datetime.utcnow)
    is_from_user: bool

    conversation: Conversation = Relationship(back_populates="messages")


#### Connection to the database

from sqlmodel import create_engine
from sqlmodel_controller import Controller
from sqlmodel import SQLModel


DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, echo=True)
# Controllers
users = Controller[User](engine=engine)
messages = Controller[ConversationMessage](engine=engine)
conversations = Controller[Conversation](engine=engine)
SQLModel.metadata.create_all(engine)
