import pytest
from src.chatbot import ChatbotService
from src import orm


@pytest.fixture
def chatbot():
    return ChatbotService(user_id=1, model="gemini-1.5-flash")


@pytest.fixture
def history():
    return [
        {"role": "user", "content": "Hello"},
        {"role": "ai", "content": "Hello"},
    ]


@pytest.fixture
def user_id():
    user_id = orm.users.create(data={"username": "test", "password": "test"})
    yield user_id
    orm.users.delete(by="id", value=user_id)


def test_send_message(chatbot):
    response = chatbot.send(message="Hello")
    assert response is not None
