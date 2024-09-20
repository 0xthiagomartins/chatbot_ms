import pytest
from nameko.standalone.rpc import ClusterRpcProxy


def test_rpc(rabbitmq_config):
    with ClusterRpcProxy(rabbitmq_config) as rpc:
        response = rpc.chatbot.send_message(
            user_id=1, model="gemini-1.5-flash", message="How to fly?"
        )
        print("=" * 10 + " OUTPUT " + "=" * 10)
        print(response)
        print("=" * 28)
        assert response is not None
