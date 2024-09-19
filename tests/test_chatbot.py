import unittest
from src.chatbot import ChatbotService


class TestChatbotService(unittest.TestCase):
    def setUp(self):
        self.chatbot = ChatbotService()

    def test_process_message(self):
        response = self.chatbot.process_message(user_id=1, message="Hello")
        self.assertIsNotNone(response)
        # Add more assertions as needed


if __name__ == "__main__":
    unittest.main()
