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


def test_lock_toggle_behavior(test_app):
    # Verify icons loaded
    assert test_app.icon_chevron is not None
    assert test_app.icon_lock is not None
    assert test_app.icon_unlock is not None

    # Verify initial unlock state on blank fields
    assert test_app.btn_lock_token is not None
    assert test_app.btn_lock_chat_id is not None
    assert test_app.entry_token.cget("state") == "normal"
    assert test_app.entry_chat_id.cget("state") == "normal"

    # Toggle token lock
    test_app.toggle_token_lock()
    assert test_app._token_locked is True
    assert test_app.entry_token.cget("state") == "readonly"
    assert test_app.entry_token.cget("text_color") == "#64748B"
    assert test_app.entry_token.cget("fg_color") == "#0D0F15"
    assert test_app.entry_token.cget("border_color") == "#1E2330"
    assert test_app.btn_lock_token.cget("fg_color") == "#1E2433"

    test_app.toggle_token_lock()
    assert test_app._token_locked is False
    assert test_app.entry_token.cget("state") == "normal"
    assert test_app.entry_token.cget("text_color") == "#F3F4F6"
    assert test_app.entry_token.cget("fg_color") == "#161922"
    assert test_app.entry_token.cget("border_color") == "#2B3345"
    assert test_app.btn_lock_token.cget("fg_color") == "#374151"

    # Toggle chat ID lock
    test_app.toggle_chat_id_lock()
    assert test_app._chat_id_locked is True
    assert test_app.entry_chat_id.cget("state") == "readonly"
    assert test_app.entry_chat_id.cget("text_color") == "#64748B"
    assert test_app.entry_chat_id.cget("fg_color") == "#0D0F15"
    assert test_app.entry_chat_id.cget("border_color") == "#1E2330"
    assert test_app.btn_lock_chat_id.cget("fg_color") == "#1E2433"

    test_app.toggle_chat_id_lock()
    assert test_app._chat_id_locked is False
    assert test_app.entry_chat_id.cget("state") == "normal"
    assert test_app.entry_chat_id.cget("text_color") == "#F3F4F6"
    assert test_app.entry_chat_id.cget("fg_color") == "#161922"
    assert test_app.entry_chat_id.cget("border_color") == "#2B3345"
    assert test_app.btn_lock_chat_id.cget("fg_color") == "#374151"


def test_clean_option_menus_chevron(test_app):
    from gui import CleanOptionMenu

    assert isinstance(test_app.opt_lang, CleanOptionMenu)
    assert isinstance(test_app.opt_display, CleanOptionMenu)
    assert isinstance(test_app.opt_hotkey, CleanOptionMenu)

    assert test_app.opt_lang.cget("button_hover_color") == "#2B3346"
    assert test_app.opt_lang._dropdown_menu.cget("borderwidth") == 0
    assert str(test_app.opt_lang._dropdown_menu.cget("relief")) == "flat"

    test_app.opt_lang._draw()
    assert len(test_app.opt_lang._canvas.find_withtag("clean_chevron")) > 0
    assert len(test_app.opt_lang._canvas.find_withtag("dropdown_arrow")) == 0
