import pytest
import customtkinter as ctk
from config import ConfigManager
from gui import MainWindow
from notifier import SoundNotifier, TelegramNotifier


@pytest.fixture(scope="module")
def test_app(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("gui_autosave_test")
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
    assert test_app.scanner is not None
    assert test_app.btn_master is not None
    assert test_app.lbl_status is not None
    assert test_app.entry_token is not None
    assert test_app.entry_chat_id is not None
    assert test_app.opt_display is not None
    assert test_app.opt_hotkey is not None
    assert test_app.chk_sound is not None
    assert test_app.btn_test is not None


def test_toggle_scanning_cycle(test_app):
    assert test_app.scanner.is_scanning is False
    test_app.on_start_toggle()
    assert test_app.scanner.is_scanning is True
    test_app.on_start_toggle()
    assert test_app.scanner.is_scanning is False


def test_language_change(test_app):
    test_app.on_language_change("English")
    assert test_app._current_lang_name == "English"
    assert test_app.cfg["language"] == "en"
    
    test_app.on_language_change("Русский")
    assert test_app._current_lang_name == "Русский"
    assert test_app.cfg["language"] == "ru"


def test_auto_save_mechanism(test_app):
    test_app.entry_token.delete(0, "end")
    test_app.entry_token.insert(0, "autosave_token_abc")
    test_app.entry_chat_id.delete(0, "end")
    test_app.entry_chat_id.insert(0, "99887766")
    
    test_app.auto_save()
    
    assert test_app.cfg["telegram_bot_token"] == "autosave_token_abc"
    assert test_app.cfg["telegram_chat_id"] == "99887766"
