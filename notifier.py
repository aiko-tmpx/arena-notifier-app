"""Notification services for AikoArenaNotifier.
Dispatches high-priority Telegram push messages and local audible host alerts.
"""

from __future__ import annotations

import datetime
import logging
import threading
import time
from typing import Optional, Tuple

import requests

try:
    import winsound
except ImportError:
    winsound = None  # Non-Windows fallback

logger = logging.getLogger("AikoArenaNotifier.Notifier")


def format_queue_pop_message(lang: str = "en") -> str:
    """Formats ultra-concise message for the Telegram arena queue pop notification."""
    if lang == "ru":
        return "🚨 ОЧЕРЕДЬ НАЙДЕНА! 🚨"
    return "🚨 QUEUE POPPED! 🚨"


def format_test_message(lang: str = "en") -> str:
    """Formats ultra-concise message for connection verification."""
    if lang == "ru":
        return "🔔 AikoArenaNotifier: Подключение проверено!"
    return "🔔 AikoArenaNotifier: Connection verified!"


class TelegramNotifier:
    """Dispatches Telegram notifications via the Telegram Bot HTTP API."""

    def __init__(self, timeout: float = 6.0) -> None:
        self.timeout = timeout

    def send_message(
        self, bot_token: str, chat_id: str, text: str
    ) -> Tuple[bool, str]:
        """Sends a Telegram message. Returns (success, status_description)."""
        token = bot_token.strip()
        chat = chat_id.strip()

        if not token:
            return False, "Telegram Bot Token is empty"
        if not chat:
            return False, "Telegram Chat ID is empty"

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            data = resp.json()

            if resp.status_code == 200 and data.get("ok"):
                return True, "OK"

            desc = data.get("description", f"HTTP {resp.status_code}")
            logger.warning(f"Telegram API responded with error: {desc}")
            return False, desc
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error in TelegramNotifier: {e}")
            return False, str(e)

    def test_connection(
        self, bot_token: str, chat_id: str, lang: str = "en"
    ) -> Tuple[bool, str]:
        """Tests bot token validity via getMe and sends a verification message."""
        token = bot_token.strip()
        chat = chat_id.strip()

        if not token:
            return False, "Telegram Bot Token is empty"
        if not chat:
            return False, "Telegram Chat ID is empty"

        # 1. Verify token with getMe
        try:
            url_me = f"https://api.telegram.org/bot{token}/getMe"
            resp_me = requests.get(url_me, timeout=self.timeout)
            data_me = resp_me.json()

            if resp_me.status_code != 200 or not data_me.get("ok"):
                desc = data_me.get("description", f"HTTP {resp_me.status_code}")
                return False, f"Invalid token: {desc}"

            bot_user = data_me.get("result", {}).get("username", "Bot")
        except requests.RequestException as e:
            return False, f"Connection failed: {e}"

        # 2. Send test alert
        test_text = format_test_message(lang)
        ok, err = self.send_message(token, chat, test_text)
        if not ok:
            return False, f"Bot @{bot_user} verified, but message failed: {err}"

        return True, f"Verified (@{bot_user})"


class SoundNotifier:
    """Manages audible notifications on the host machine using PC speaker / winsound."""

    def play_pop_sound(self, enabled: bool = True, blocking: bool = False) -> None:
        """Plays a multi-frequency audible chime when a queue pop is detected."""
        if not enabled:
            return

        def _play():
            try:
                if winsound:
                    # Chime pattern: 1200Hz -> 1600Hz -> 2000Hz
                    winsound.Beep(1200, 120)
                    time.sleep(0.03)
                    winsound.Beep(1600, 120)
                    time.sleep(0.03)
                    winsound.Beep(2000, 220)
            except Exception as e:
                logger.debug(f"Failed to play winsound beep: {e}")

        if blocking:
            _play()
        else:
            threading.Thread(target=_play, daemon=True, name="SoundThread").start()

    def play_test_sound(self) -> None:
        """Plays a short test tone."""
        def _play():
            try:
                if winsound:
                    winsound.Beep(1400, 150)
            except Exception:
                pass

        threading.Thread(target=_play, daemon=True, name="SoundTestThread").start()
