import pytest
from src.chatbot import ChatbotService
from src import orm


@pytest.fixture
def chatbot():
    return ChatbotService(user_id=1)


@pytest.fixture(scope="module")
def user_id():
    user_id = orm.users.upsert(
        by="username",
        value="username",
        data={
            "username": "username",
            "email": "email@email.com",
            "hashed_password": "test",
        },
    )
    return user_id


def _display(*args, **kwargs):
    print("-~" * 10 + " MESSAGE " + "-~" * 10, end="\n\t")
    print(*args, **kwargs)


def test_send_messages(user_id):
    chatbot = ChatbotService(user_id=user_id)
    messages = (
        "Tell me a good joke",
        "Tell me another joke",
        "What was the first message that I've send to you?",
    )
    responses = []
    for msg in messages:
        response = chatbot.send(message=msg, model="gemini-1.5-flash")
        assert response is not None
        responses.append(response)

    for i in range(0, len(messages)):
        _display(messages[i].replace("\n", "\n\t"))
        _display(responses[i].replace("\n", "\n\t"))
