import json
import os
from pathlib import Path
import pytest
from config import ConfigManager, DEFAULT_CONFIG


def test_default_config_values():
    assert "telegram_bot_token" in DEFAULT_CONFIG
    assert "telegram_chat_id" in DEFAULT_CONFIG
    assert DEFAULT_CONFIG["selected_display_index"] == 0
    assert DEFAULT_CONFIG["hotkey"] == "F9"
    assert DEFAULT_CONFIG["sound_enabled"] is True
    assert DEFAULT_CONFIG["language"] in ("en", "ru")


def test_load_config_when_file_does_not_exist(tmp_path):
    config_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=config_file)
    cfg = mgr.load_config()
    assert cfg == DEFAULT_CONFIG


def test_save_and_reload_config(tmp_path):
    config_file = tmp_path / "config.json"
    mgr = ConfigManager(config_path=config_file)
    
    updated = {
        "telegram_bot_token": "123456:ABC-DEF",
        "telegram_chat_id": "987654321",
        "selected_display_index": 1,
        "hotkey": "F10",
        "sound_enabled": False,
        "language": "ru",
    }
    mgr.save_config(updated)
    
    # Verify file was written to disk
    assert config_file.exists()
    
    # Reload and verify
    reloaded = mgr.load_config()
    for k, v in updated.items():
        assert reloaded[k] == v


def test_config_preserves_defaults_for_missing_keys(tmp_path):
    config_file = tmp_path / "config.json"
    partial_data = {
        "telegram_bot_token": "token123"
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(partial_data, f)
        
    mgr = ConfigManager(config_path=config_file)
    loaded = mgr.load_config()
    assert loaded["telegram_bot_token"] == "token123"
    assert loaded["telegram_chat_id"] == DEFAULT_CONFIG["telegram_chat_id"]
    assert loaded["hotkey"] == "F9"
    assert loaded["sound_enabled"] is True


def test_resolve_default_path():
    mgr = ConfigManager()
    path = mgr.get_config_path()
    assert isinstance(path, Path)
    assert path.name == "config.json"
