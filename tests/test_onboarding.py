import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lunch_bot
from api.index import app


class TestOnboardingLogic(unittest.TestCase):

    def setUp(self):
        # Configure stdout to handle emojis
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    @patch("lunch_bot.get_redis_client")
    @patch.dict(os.environ, {"REGULARS": "alice,bob,@charlie"})
    def test_get_regulars_migration_fallback(self, mock_get_redis_client):
        """Test fallback and migration when Redis key does not exist."""
        # Mock Redis exists() to return False (no key yet)
        mock_redis = MagicMock()
        mock_redis.exists.return_value = False
        mock_get_redis_client.return_value = mock_redis

        # Retrieve regulars
        regulars = lunch_bot.get_regulars()

        # Check migration logic called
        mock_redis.exists.assert_called_with("regulars")
        mock_redis.sadd.assert_called_once_with("regulars", "alice", "bob", "charlie")
        self.assertEqual(sorted(regulars), ["alice", "bob", "charlie"])

    @patch("lunch_bot.get_redis_client")
    def test_get_regulars_existing_redis(self, mock_get_redis_client):
        """Test retrieval when Redis key already exists."""
        mock_redis = MagicMock()
        mock_redis.exists.return_value = True
        mock_redis.smembers.return_value = {"dave", "eva"}
        mock_get_redis_client.return_value = mock_redis

        regulars = lunch_bot.get_regulars()

        mock_redis.exists.assert_called_with("regulars")
        self.assertEqual(sorted(regulars), ["dave", "eva"])

    @patch("lunch_bot.get_redis_client")
    def test_add_and_remove_regular(self, mock_get_redis_client):
        """Test adding and removing a regular from Redis."""
        mock_redis = MagicMock()
        mock_redis.exists.return_value = True
        mock_get_redis_client.return_value = mock_redis

        # Add
        success_add = lunch_bot.add_regular("@Frank")
        self.assertTrue(success_add)
        mock_redis.sadd.assert_called_once_with("regulars", "frank")

        # Remove
        success_remove = lunch_bot.remove_regular("Frank")
        self.assertTrue(success_remove)
        mock_redis.srem.assert_called_once_with("regulars", "frank")


class TestWebhookOnboarding(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("lunch_bot.get_redis_client")
    @patch("lunch_bot.get_ai_hype")
    @patch("lunch_bot.send_telegram_message")
    def test_new_chat_member_webhook(self, mock_send_msg, mock_get_hype, mock_get_redis_client):
        """Test that new_chat_members webhook adds user and celebrates."""
        mock_redis = MagicMock()
        mock_redis.exists.return_value = True
        mock_get_redis_client.return_value = mock_redis
        mock_get_hype.return_value = "MOCK CELEBRATION! 🎉"

        payload = {
            "update_id": 12345,
            "message": {
                "message_id": 100,
                "chat": {"id": -100123, "type": "supergroup"},
                "new_chat_members": [
                    {"id": 999, "is_bot": False, "username": "new_guy", "first_name": "New Guy"}
                ]
            }
        }

        response = self.app.post("/", json=payload)
        self.assertEqual(response.status_code, 200)

        # Verify Redis add and AI Hype sent
        mock_redis.sadd.assert_called_once_with("regulars", "new_guy")
        mock_get_hype.assert_called_with(prompt_type="onboard", user_query="@new_guy")
        mock_send_msg.assert_called_with("MOCK CELEBRATION! 🎉", chat_id=-100123)

    @patch("lunch_bot.get_redis_client")
    @patch("lunch_bot.get_ai_hype")
    @patch("lunch_bot.send_telegram_message")
    def test_left_chat_member_webhook(self, mock_send_msg, mock_get_hype, mock_get_redis_client):
        """Test that left_chat_member webhook removes user and says goodbye."""
        mock_redis = MagicMock()
        mock_redis.exists.return_value = True
        mock_get_redis_client.return_value = mock_redis
        mock_get_hype.return_value = "MOCK GOODBYE! 😢"

        payload = {
            "update_id": 12346,
            "message": {
                "message_id": 101,
                "chat": {"id": -100123, "type": "supergroup"},
                "left_chat_member": {"id": 999, "is_bot": False, "username": "old_guy", "first_name": "Old Guy"}
            }
        }

        response = self.app.post("/", json=payload)
        self.assertEqual(response.status_code, 200)

        # Verify Redis remove and AI Hype sent
        mock_redis.srem.assert_called_once_with("regulars", "old_guy")
        mock_get_hype.assert_called_with(prompt_type="offboard", user_query="@old_guy")
        mock_send_msg.assert_called_with("MOCK GOODBYE! 😢", chat_id=-100123)

    @patch("lunch_bot.get_redis_client")
    @patch("lunch_bot.get_ai_hype")
    @patch("lunch_bot.send_telegram_message")
    def test_join_command_webhook(self, mock_send_msg, mock_get_hype, mock_get_redis_client):
        """Test /join command webhooks (explicit and self)."""
        mock_redis = MagicMock()
        mock_redis.exists.return_value = True
        mock_get_redis_client.return_value = mock_redis
        mock_get_hype.return_value = "MOCK CELEBRATION! 🎉"

        # Case 1: Self-join command
        payload_self = {
            "update_id": 12347,
            "message": {
                "message_id": 102,
                "from": {"id": 111, "username": "sender_user"},
                "chat": {"id": -100123, "type": "supergroup"},
                "text": "/join"
            }
        }
        response = self.app.post("/", json=payload_self)
        self.assertEqual(response.status_code, 200)
        mock_redis.sadd.assert_called_with("regulars", "sender_user")
        mock_get_hype.assert_called_with(prompt_type="onboard", user_query="@sender_user")

        # Case 2: Onboard explicit command (/onboard @other_user)
        payload_explicit = {
            "update_id": 12348,
            "message": {
                "message_id": 103,
                "from": {"id": 111, "username": "sender_user"},
                "chat": {"id": -100123, "type": "supergroup"},
                "text": "/onboard @other_user"
            }
        }
        response = self.app.post("/", json=payload_explicit)
        self.assertEqual(response.status_code, 200)
        mock_redis.sadd.assert_called_with("regulars", "other_user")
        mock_get_hype.assert_called_with(prompt_type="onboard", user_query="@other_user")


if __name__ == "__main__":
    unittest.main()
