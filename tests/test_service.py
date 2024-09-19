import unittest
from src.service import ChatService


class TestChatService(unittest.TestCase):
    def setUp(self):
        self.service = ChatService()

    def test_send_message(self):
        response = self.service.send_message(user_id=1, message="Hello")
        self.assertIsNotNone(response)
        # Add more assertions as needed


if __name__ == "__main__":
    unittest.main()
