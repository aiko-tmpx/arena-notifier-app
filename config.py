"""Configuration manager for AikoArenaNotifier.
Handles persistent JSON settings with fallback defaults and graceful error recovery.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "selected_display_index": 0,
    "sound_enabled": True,
    "scan_interval_ms": 300,
    "tolerance": 25,
    "language": "en",
}


class ConfigManager:
    """Manages loading and saving application configuration."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        if config_path:
            self._path = Path(config_path)
        else:
            self._path = self._resolve_default_path()

    @staticmethod
    def _resolve_default_path() -> Path:
        """Determines best storage path: local working dir or APPDATA."""
        local_path = Path("config.json")
        if local_path.exists():
            return local_path

        appdata = os.getenv("APPDATA")
        if appdata:
            dir_path = Path(appdata) / "AikoArenaNotifier"
            return dir_path / "config.json"

        return local_path

    def get_config_path(self) -> Path:
        """Returns the active configuration file path."""
        return self._path

    def load_config(self) -> Dict[str, Any]:
        """Loads configuration from disk, falling back to defaults for missing keys."""
        if not self._path.exists():
            return dict(DEFAULT_CONFIG)

        try:
            with open(self._path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            if not isinstance(loaded, dict):
                return dict(DEFAULT_CONFIG)

            config = dict(DEFAULT_CONFIG)
            config.update(loaded)
            return config
        except (json.JSONDecodeError, OSError):
            return dict(DEFAULT_CONFIG)

    def save_config(self, data: Dict[str, Any]) -> bool:
        """Saves configuration to disk with formatted JSON."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            current = self.load_config()
            current.update(data)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=4, ensure_ascii=False)
            return True
        except OSError:
            return False
