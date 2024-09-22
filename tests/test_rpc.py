import pytest
from nameko.standalone.rpc import ClusterRpcProxy
from rich import print
from time import sleep
import threading


def test_rpc(rabbitmq_config):
    with ClusterRpcProxy(rabbitmq_config) as rpc:
        response = rpc.chatbot.send_message(
            user_id=1, model="gemini-1.5-flash", message="How to fly?"
        )
        print("=" * 10 + " OUTPUT " + "=" * 10)
        print(response)
        print("=" * 28)
        assert response is not None


def test_stream_consumer_and_producer(rabbitmq_config):
    # two threads consume from stream_queue
    # one thread sends a message to stream_queue
    # the other thread receives the message and stores it
    # the message is a list of chunks
    # the chunks are dictionaries with the following keys:
    # - content: str
    # - type: str "ai"
    # - user_id: int
    # - conversation_id: int
    with ClusterRpcProxy(rabbitmq_config) as rpc:

        def produce_message(rpc):
            rpc.chatbot.send_streamed_message(
                user_id=1,
                model="gemini-1.5-flash",
                message="Write a story about a cat that died at the first wednesday of his life",
            )

        def consume_message(rpc):
            while produce_thread.is_alive():
                received_messages = rpc.chatbot.get_received_messages()
                print("=" * 10 + " OUTPUT " + "=" * 10, flush=True)
                print(received_messages, flush=True)
                print("=" * 28, flush=True)
                sleep(1)  # Add a small delay to avoid spamming the output

        with ClusterRpcProxy(rabbitmq_config) as rpc:
            produce_thread = threading.Thread(
                target=produce_message,
                args=(rpc,),
            )
            consume_thread = threading.Thread(
                target=consume_message,
                args=(rpc,),
            )

            produce_thread.start()
            consume_thread.start()

            produce_thread.join()
            consume_thread.join()
            # wait until produce_thread is done
            sleep(1.5)
            received_messages = rpc.chatbot.get_received_messages()
            print("=" * 10 + " FINAL OUTPUT " + "=" * 10, flush=True)
            print(received_messages, flush=True)
            print("=" * 28, flush=True)
            assert len(received_messages) > 0
            assert received_messages[0]["content"] == "How to fly?"
            assert received_messages[0]["type"] == "ai"
            assert received_messages[0]["user_id"] == 1
            assert received_messages[0]["conversation_id"] == 1
