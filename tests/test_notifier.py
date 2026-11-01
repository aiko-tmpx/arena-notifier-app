from unittest.mock import MagicMock, patch
import pytest
import requests
from notifier import (
    TelegramNotifier,
    SoundNotifier,
    format_queue_pop_message,
)


def test_format_queue_pop_message():
    msg = format_queue_pop_message()
    assert "ARENA QUEUE" in msg
    assert "World of Warcraft" in msg
    assert "Enter battle" in msg


def test_telegram_send_empty_token_or_chat():
    notifier = TelegramNotifier()
    ok, err = notifier.send_message("", "12345", "test")
    assert ok is False
    assert "Token" in err

    ok, err = notifier.send_message("12345:token", "", "test")
    assert ok is False
    assert "Chat ID" in err


@patch("requests.post")
def test_telegram_send_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 101}}
    mock_post.return_value = mock_resp

    notifier = TelegramNotifier()
    ok, err = notifier.send_message("dummy_token", "123456", "Hello")

    assert ok is True
    assert err == "OK"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "https://api.telegram.org/botdummy_token/sendMessage" in args[0]
    assert kwargs["json"]["chat_id"] == "123456"
    assert kwargs["json"]["text"] == "Hello"
    assert kwargs["json"]["parse_mode"] == "Markdown"


@patch("requests.post")
def test_telegram_send_api_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.json.return_value = {"ok": False, "description": "Unauthorized"}
    mock_post.return_value = mock_resp

    notifier = TelegramNotifier()
    ok, err = notifier.send_message("invalid_token", "123456", "Hello")

    assert ok is False
    assert "Unauthorized" in err


@patch("requests.post")
def test_telegram_send_connection_error(mock_post):
    mock_post.side_effect = requests.RequestException("Connection timed out")

    notifier = TelegramNotifier()
    ok, err = notifier.send_message("dummy_token", "123456", "Hello")

    assert ok is False
    assert "Connection timed out" in err


@patch("requests.get")
@patch.object(TelegramNotifier, "send_message")
def test_telegram_test_connection_success(mock_send, mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True, "result": {"username": "ArenaBot"}}
    mock_get.return_value = mock_resp
    mock_send.return_value = (True, "OK")

    notifier = TelegramNotifier()
    ok, err = notifier.test_connection("dummy_token", "123456")

    assert ok is True
    assert "ArenaBot" in err or "success" in err.lower() or err == "OK"


def test_sound_notifier_disabled():
    sound = SoundNotifier()
    # When enabled is False, should return immediately without playing sound
    sound.play_pop_sound(enabled=False, blocking=True)
