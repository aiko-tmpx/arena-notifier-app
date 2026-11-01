import pytest
import customtkinter as ctk
from config import ConfigManager
from gui import MainWindow
from notifier import SoundNotifier, TelegramNotifier


@pytest.fixture(scope="module")
def test_app(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("gui_test")
    config_file = tmp_path / "config.json"
    cfg_mgr = ConfigManager(config_path=config_file)
    tg = TelegramNotifier()
    sound = SoundNotifier()
    
    app = MainWindow(cfg_mgr, tg, sound)
    app.withdraw()  # Keep window hidden during test
    yield app
    try:
        app.on_closing()
    except Exception:
        pass


def test_main_window_initialization(test_app):
    assert test_app.title() == "AikoArenaNotifier"
    assert "dashboard" in test_app.views
    assert "settings" in test_app.views
    assert "guide" in test_app.views
    assert test_app.scanner is not None


def test_switch_views(test_app):
    test_app.switch_view("settings")
    test_app.switch_view("guide")
    test_app.switch_view("dashboard")


def test_toggle_scanning_cycle(test_app):
    assert test_app.scanner.is_scanning is False
    test_app.toggle_scanning()
    assert test_app.scanner.is_scanning is True
    test_app.toggle_scanning()
    assert test_app.scanner.is_scanning is False


def test_log_event(test_app):
    test_app.log_event("Integration test log entry")
    content = test_app.log_textbox.get("1.0", "end")
    assert "Integration test log entry" in content
