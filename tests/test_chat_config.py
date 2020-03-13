from datetime import datetime
import unittest

from chat_config import ChatConfig


class TestChatConfig(unittest.TestCase):
    def test_create_default_chat_config(self):
        chat = ChatConfig()
        self.assertEqual(chat.hour, 0)
        self.assertEqual(chat.days, "weekdays")
        self.assertEqual(chat.chat_id, "")

    def test_update_username(self):
        chat = ChatConfig()
        chat.update(username="devmob")
        self.assertEqual(chat.username, "devmob")

    def test_update_hour(self):
        chat = ChatConfig()
        chat.update(hour=9)
        self.assertEqual(chat.hour, 9)

    def test_update_days(self):
        chat = ChatConfig()
        chat.update(days="weekdays")
        self.assertEqual(chat.days, "weekdays")

    def test_update_default_to_invalid_days(self):
        chat = ChatConfig()
        chat.update(days="today")
        self.assertEqual(chat.days, "weekdays")

    def test_update_chained_fields(self):
        chat = ChatConfig()
        chat.update(days="daily")
        chat.update(hour=12)
        self.assertEqual(chat.days, "daily")
        self.assertEqual(chat.hour, 12)

    def test_update_multiple_fields(self):
        chat = ChatConfig()
        chat.update(days="weekdays", username="devmob", hour=14)
        self.assertEqual(chat.days, "weekdays")
        self.assertEqual(chat.username, "devmob")
        self.assertEqual(chat.hour, 14)

    def test_empty_chat_is_not_valid(self):
        chat = ChatConfig()
        self.assertFalse(chat.valid())

    def test_chat_is_valid(self):
        chat = ChatConfig(username="devmob", chat_id="123abc")
        self.assertTrue(chat.valid())

    def test_should_not_send_message_wrong_hour(self):
        chat = ChatConfig(days="daily", hour=(datetime.utcnow().hour + 2) % 24,
                          username="devmob", chat_id="abc123")
        self.assertFalse(chat.should_send_message())

    def test_should_not_send_message_no_username(self):
        chat = ChatConfig(days="daily", hour=(datetime.utcnow().hour + 2) % 24,
                          username="", chat_id="abc123")
        self.assertFalse(chat.should_send_message())

    def test_should_not_send_message_chat_id(self):
        chat = ChatConfig(days="daily", hour=datetime.utcnow().hour,
                          username="abcs", chat_id="")
        self.assertFalse(chat.should_send_message())

    def test_should_send_message_daily(self):
        chat = ChatConfig(days="daily", hour=datetime.utcnow().hour,
                          username="devmob", chat_id="abc123")
        self.assertTrue(chat.should_send_message())

    def test_should_send_message_weekdays(self):
        chat = ChatConfig(days="weekdays", hour=datetime.utcnow().hour,
                          username="devmob", chat_id="pipipi")
        if datetime.utcnow().weekday() < 5:
            self.assertTrue(chat.should_send_message())
        else:
            self.assertFalse(chat.should_send_message())


if __name__ == '__main__':
    unittest.main()
