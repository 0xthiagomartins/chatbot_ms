import pytest
from nameko.standalone.rpc import ClusterRpcProxy


def test_rpc_speedtest(rabbitmq_config):
    with ClusterRpcProxy(rabbitmq_config) as rpc:
        response = rpc.chatbot.send_message(
            user_id=1, model="gemini-1.5-flash", message="Hello"
        )
        assert response is not None
