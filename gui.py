"""Spacious, single-window compact desktop utility for AikoArenaNotifier.
Features Inter typography, strict grid layout, and seamless backend wiring.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
from typing import Dict, List, Optional, Tuple

import customtkinter as ctk

from config import ConfigManager
from localization import t
from notifier import SoundNotifier, TelegramNotifier, format_queue_pop_message
from scanner import ScreenScanner, get_monitors

logger = logging.getLogger("AikoArenaNotifier.GUI")

# UI Palette Constants
COLOR_BG = "#0F1117"
COLOR_SURFACE_ALT = "#161922"
COLOR_INPUT_BORDER = "#2B3345"
COLOR_DIVIDER = "#2D3343"
COLOR_ACCENT = "#7C3AED"
COLOR_ACCENT_HOVER = "#6D28D9"
COLOR_SCANNING = "#059669"
COLOR_SCANNING_HOVER = "#047857"
COLOR_SECONDARY_BTN = "#374151"
COLOR_SECONDARY_BTN_HOVER = "#4B5563"
COLOR_TEXT_PRIMARY = "#F3F4F6"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_TEXT_DIM = "#6B7280"
COLOR_STATUS_ACTIVE = "#10B981"
COLOR_DANGER = "#EF4444"

FONT_FAMILY = "Inter"


class MainWindow(ctk.CTk):
    """Compact Single-Window Utility for AikoArenaNotifier."""

    def __init__(
        self,
        config_manager: ConfigManager,
        telegram_notifier: TelegramNotifier,
        sound_notifier: SoundNotifier,
    ) -> None:
        super().__init__()

        self.config_manager = config_manager
        self.telegram_notifier = telegram_notifier
        self.sound_notifier = sound_notifier
        self.cfg = self.config_manager.load_config()

        # Keyboard hotkey hook tracker
        self._hotkey_hook = None
        self._current_hotkey = self.cfg.get("hotkey", "F9")

        # Window dimensions: Fixed 540x680 px
        self.title("AikoArenaNotifier")
        self.geometry("540x680")
        self.minsize(540, 680)
        self.maxsize(540, 680)
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Set Window Icon
        self._set_window_icon()

        # Monitored display list
        self.monitors = get_monitors()

        # Typography Scale
        self._init_typography()

        # Scanner initialization
        display_idx = self.cfg.get("selected_display_index", 0)
        if display_idx >= len(self.monitors):
            display_idx = 0
        self.scanner = ScreenScanner(
            display_index=display_idx,
            interval_ms=self.cfg.get("scan_interval_ms", 300),
            on_tick=self._on_scanner_tick,
            on_pop=self._on_scanner_pop,
        )

        # Build Strict Grid Layout
        self._setup_layout()

        # Bind initial global hotkey
        self._register_global_hotkey(self._current_hotkey)

    def _set_window_icon(self) -> None:
        """Sets application window icon from assets/icon.ico if available."""
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _init_typography(self) -> None:
        """Initializes typography scale using Inter with smooth fallback."""
        self.font_btn_main = ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        self.font_subtitle = ctk.CTkFont(family=FONT_FAMILY, size=13)
        self.font_form_label = ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")
        self.font_input = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.font_checkbox = ctk.CTkFont(family=FONT_FAMILY, size=13)
        self.font_btn_action = ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        self.font_footer = ctk.CTkFont(family=FONT_FAMILY, size=12)

    def _setup_layout(self) -> None:
        """Constructs compact single-window layout using strictly .grid()."""
        lang = self.cfg.get("language", "ru")

        # Root grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main wrapper frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=32, pady=24)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # ROW 0: Master Action Button
        self.btn_master = ctk.CTkButton(
            self.main_frame,
            text=self._get_master_button_text(is_scanning=False),
            font=self.font_btn_main,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            height=56,
            corner_radius=10,
            command=self.on_start_toggle,
        )
        self.btn_master.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # ROW 1: Status Subtitle
        self.lbl_status = ctk.CTkLabel(
            self.main_frame,
            text=self._get_status_subtitle_text(is_scanning=False),
            font=self.font_subtitle,
            text_color=COLOR_TEXT_MUTED,
            anchor="center",
        )
        self.lbl_status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # ROW 2: Separator
        sep1 = ctk.CTkFrame(self.main_frame, height=1, fg_color=COLOR_DIVIDER)
        sep1.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # ROW 3: Form - Language Label
        self.lbl_lang = ctk.CTkLabel(
            self.main_frame,
            text=t("field_lang_label", lang),
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_lang.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ROW 4: Form - Language OptionMenu
        current_lang_str = "Русский" if lang == "ru" else "English"
        self.opt_lang = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Русский", "English"],
            font=self.font_input,
            height=40,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            button_color="#232734",
            button_hover_color=COLOR_ACCENT,
            command=self.on_language_change,
        )
        self.opt_lang.set(current_lang_str)
        self.opt_lang.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # ROW 5: Form - Telegram Bot Token Label
        self.lbl_token = ctk.CTkLabel(
            self.main_frame,
            text=t("field_token_label", lang),
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_token.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ROW 6: Form - Telegram Bot Token Entry
        self.entry_token = ctk.CTkEntry(
            self.main_frame,
            show="*",
            font=self.font_input,
            height=40,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_token.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        if self.cfg.get("telegram_bot_token"):
            self.entry_token.insert(0, self.cfg["telegram_bot_token"])

        # ROW 7: Form - Telegram Chat ID Label
        self.lbl_chat_id = ctk.CTkLabel(
            self.main_frame,
            text=t("field_chat_id_label", lang),
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_chat_id.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ROW 8: Form - Telegram Chat ID Entry
        self.entry_chat_id = ctk.CTkEntry(
            self.main_frame,
            font=self.font_input,
            height=40,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_chat_id.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        if self.cfg.get("telegram_chat_id"):
            self.entry_chat_id.insert(0, str(self.cfg["telegram_chat_id"]))

        # ROW 9: Form - Target Game Display Label
        self.lbl_display = ctk.CTkLabel(
            self.main_frame,
            text=t("field_display_label", lang),
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_display.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ROW 10: Form - Target Game Display OptionMenu
        monitor_labels = [m["label"] for m in self.monitors]
        selected_mon_idx = self.cfg.get("selected_display_index", 0)
        default_mon_label = (
            monitor_labels[selected_mon_idx]
            if 0 <= selected_mon_idx < len(monitor_labels)
            else monitor_labels[0]
        )

        self.opt_display = ctk.CTkOptionMenu(
            self.main_frame,
            values=monitor_labels,
            font=self.font_input,
            height=40,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            button_color="#232734",
            button_hover_color=COLOR_ACCENT,
        )
        self.opt_display.set(default_mon_label)
        self.opt_display.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # ROW 11: Form - Hotkey Label
        self.lbl_hotkey = ctk.CTkLabel(
            self.main_frame,
            text=t("field_hotkey_label", lang),
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_hotkey.grid(row=11, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ROW 12: Form - Hotkey OptionMenu
        hotkey_options = ["F8", "F9", "F10", "F11", "F12"]
        current_hk = self.cfg.get("hotkey", "F9")
        if current_hk not in hotkey_options:
            hotkey_options.append(current_hk)

        self.opt_hotkey = ctk.CTkOptionMenu(
            self.main_frame,
            values=hotkey_options,
            font=self.font_input,
            height=40,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            button_color="#232734",
            button_hover_color=COLOR_ACCENT,
        )
        self.opt_hotkey.set(current_hk)
        self.opt_hotkey.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # ROW 13: Form - Host Audio Alert Checkbox
        self.chk_sound = ctk.CTkCheckBox(
            self.main_frame,
            text=t("field_sound_label", lang),
            font=self.font_checkbox,
            text_color=COLOR_TEXT_PRIMARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
        )
        if self.cfg.get("sound_enabled", True):
            self.chk_sound.select()
        else:
            self.chk_sound.deselect()
        self.chk_sound.grid(row=13, column=0, columnspan=2, sticky="w", pady=(4, 16))

        # ROW 14: Separator
        sep2 = ctk.CTkFrame(self.main_frame, height=1, fg_color=COLOR_DIVIDER)
        sep2.grid(row=14, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # ROW 15: Footer Action Buttons
        self.btn_test = ctk.CTkButton(
            self.main_frame,
            text=t("btn_test_telegram", lang),
            font=self.font_btn_action,
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_BTN_HOVER,
            height=44,
            corner_radius=8,
            command=self.on_test_connection,
        )
        self.btn_test.grid(row=15, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        self.btn_save = ctk.CTkButton(
            self.main_frame,
            text=t("btn_save_settings", lang),
            font=self.font_btn_action,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=44,
            corner_radius=8,
            command=self.on_save_settings,
        )
        self.btn_save.grid(row=15, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        # ROW 16: Inline Status Notification
        self.lbl_feedback = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=self.font_footer,
            text_color=COLOR_TEXT_MUTED,
            anchor="center",
        )
        self.lbl_feedback.grid(row=16, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        # ROW 17: Quick Hint Footer
        self.lbl_hint = ctk.CTkLabel(
            self.main_frame,
            text=t("quick_hint", lang),
            font=self.font_footer,
            text_color=COLOR_TEXT_DIM,
            anchor="center",
        )
        self.lbl_hint.grid(row=17, column=0, columnspan=2, sticky="ew")

    # =========================================================================
    # HANDLERS & STATE CONTROLLER
    # =========================================================================
    def on_start_toggle(self) -> None:
        """Toggles scanner state between IDLE and SCANNING."""
        if self.scanner.is_scanning:
            self.stop_scanning()
        else:
            self.start_scanning()

    def toggle_scanning(self) -> None:
        """Alias for hotkey invocation."""
        self.on_start_toggle()

    def start_scanning(self) -> None:
        """Arms scanner and transitions UI to SCANNING state."""
        if self.scanner.start():
            self._update_ui_state(is_scanning=True)

    def stop_scanning(self) -> None:
        """Disarms scanner and transitions UI to IDLE state."""
        self.scanner.stop()
        self._update_ui_state(is_scanning=False)

    def _update_ui_state(self, is_scanning: bool) -> None:
        """Updates master button and status subtitle."""
        self.btn_master.configure(
            text=self._get_master_button_text(is_scanning),
            fg_color=COLOR_SCANNING if is_scanning else COLOR_ACCENT,
            hover_color=COLOR_SCANNING_HOVER if is_scanning else COLOR_ACCENT_HOVER,
        )
        self.lbl_status.configure(
            text=self._get_status_subtitle_text(is_scanning),
            text_color=COLOR_STATUS_ACTIVE if is_scanning else COLOR_TEXT_MUTED,
        )

    def _get_master_button_text(self, is_scanning: bool) -> str:
        """Returns localized master action button text."""
        lang = self.cfg.get("language", "ru")
        key = "btn_monitoring_active" if is_scanning else "btn_monitoring_idle"
        return t(key, lang, hotkey=self._current_hotkey)

    def _get_status_subtitle_text(self, is_scanning: bool) -> str:
        """Returns localized status subtitle text."""
        lang = self.cfg.get("language", "ru")
        key = "status_subtitle_scanning" if is_scanning else "status_subtitle_idle"
        return t(key, lang)

    def _on_scanner_tick(self, rgb: Tuple[int, int, int]) -> None:
        """Scanner tick hook."""
        pass

    def _on_scanner_pop(self) -> None:
        """Invoked when pop marker is detected. Marshals to GUI thread."""
        self.after(0, self._handle_queue_pop)

    def _handle_queue_pop(self) -> None:
        """Handles queue pop: auto-stop, audio chime, Telegram alert, and status."""
        lang = self.cfg.get("language", "ru")
        self._update_ui_state(is_scanning=False)

        # 1. Local PC sound alert
        if self.cfg.get("sound_enabled", True):
            self.sound_notifier.play_pop_sound(enabled=True)

        # 2. Telegram push notification
        token = self.cfg.get("telegram_bot_token", "").strip()
        chat_id = self.cfg.get("telegram_chat_id", "").strip()

        if token and chat_id:
            def _send_worker():
                msg = format_queue_pop_message(lang)
                ok, err = self.telegram_notifier.send_message(token, chat_id, msg)
                self.after(0, self._on_telegram_result, ok, err)

            threading.Thread(target=_send_worker, daemon=True, name="TgSendThread").start()

    def _on_telegram_result(self, ok: bool, err_msg: str) -> None:
        """Updates feedback label on Telegram send outcome."""
        lang = self.cfg.get("language", "ru")
        if ok:
            self.lbl_feedback.configure(
                text=t("status_test_success", lang),
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_feedback.configure(
                text=t("status_test_failed", lang, error=err_msg),
                text_color=COLOR_DANGER,
            )

    # =========================================================================
    # SETTINGS & ACTION HANDLERS
    # =========================================================================
    def on_test_connection(self) -> None:
        """Tests Telegram connection in background thread."""
        lang = self.cfg.get("language", "ru")
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token:
            self.lbl_feedback.configure(
                text=t("status_token_empty", lang),
                text_color=COLOR_DANGER,
            )
            return

        if not chat_id:
            self.lbl_feedback.configure(
                text=t("status_chat_id_empty", lang),
                text_color=COLOR_DANGER,
            )
            return

        self.lbl_feedback.configure(
            text=t("status_testing_connection", lang),
            text_color=COLOR_ACCENT,
        )
        self.btn_test.configure(state="disabled")

        def _test_worker():
            ok, msg = self.telegram_notifier.test_connection(token, chat_id, lang)
            self.after(0, self._on_test_finished, ok, msg)

        threading.Thread(target=_test_worker, daemon=True, name="TgTestThread").start()

    def _on_test_finished(self, ok: bool, msg: str) -> None:
        """Handles completion of Telegram connection test."""
        lang = self.cfg.get("language", "ru")
        self.btn_test.configure(state="normal")

        if ok:
            self.lbl_feedback.configure(
                text=f"{t('status_test_success', lang)} ({msg})",
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_feedback.configure(
                text=t("status_test_failed", lang, error=msg),
                text_color=COLOR_DANGER,
            )

    def on_save_settings(self) -> None:
        """Saves current inputs to config.json and updates runtime state."""
        lang = self.cfg.get("language", "ru")
        new_token = self.entry_token.get().strip()
        new_chat_id = self.entry_chat_id.get().strip()
        new_hotkey = self.opt_hotkey.get().strip()
        new_sound = bool(self.chk_sound.get())

        selected_label = self.opt_display.get()
        selected_idx = 0
        for idx, m in enumerate(self.monitors):
            if m["label"] == selected_label:
                selected_idx = idx
                break

        updated_data = {
            "telegram_bot_token": new_token,
            "telegram_chat_id": new_chat_id,
            "selected_display_index": selected_idx,
            "hotkey": new_hotkey,
            "sound_enabled": new_sound,
        }

        success = self.config_manager.save_config(updated_data)
        if success:
            self.cfg = self.config_manager.load_config()
            self.scanner.display_index = selected_idx

            if new_hotkey != self._current_hotkey:
                self._register_global_hotkey(new_hotkey)

            self._update_ui_state(is_scanning=self.scanner.is_scanning)

            self.lbl_feedback.configure(
                text=t("status_saved_success", lang),
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_feedback.configure(
                text=t("status_saved_failed", lang),
                text_color=COLOR_DANGER,
            )

    def on_language_change(self, selected_lang: str) -> None:
        """Switches UI language dynamically and persists selection."""
        new_lang = "ru" if selected_lang == "Русский" else "en"
        self.cfg["language"] = new_lang
        self.config_manager.save_config({"language": new_lang})

        # Update all UI texts
        self.lbl_lang.configure(text=t("field_lang_label", new_lang))
        self.lbl_token.configure(text=t("field_token_label", new_lang))
        self.lbl_chat_id.configure(text=t("field_chat_id_label", new_lang))
        self.lbl_display.configure(text=t("field_display_label", new_lang))
        self.lbl_hotkey.configure(text=t("field_hotkey_label", new_lang))
        self.chk_sound.configure(text=t("field_sound_label", new_lang))
        self.btn_test.configure(text=t("btn_test_telegram", new_lang))
        self.btn_save.configure(text=t("btn_save_settings", new_lang))
        self.lbl_hint.configure(text=t("quick_hint", new_lang))

        self._update_ui_state(is_scanning=self.scanner.is_scanning)

    # =========================================================================
    # GLOBAL HOTKEY MANAGEMENT
    # =========================================================================
    def _register_global_hotkey(self, hotkey_str: str) -> None:
        """Safely binds global toggle hotkey using keyboard library."""
        try:
            import keyboard

            if self._hotkey_hook:
                try:
                    keyboard.remove_hotkey(self._hotkey_hook)
                except Exception:
                    pass

            self._hotkey_hook = keyboard.add_hotkey(
                hotkey_str,
                lambda: self.after(0, self.on_start_toggle),
            )
            self._current_hotkey = hotkey_str
        except Exception as e:
            logger.warning(f"Could not register hotkey {hotkey_str}: {e}")

    def on_closing(self) -> None:
        """Performs clean shutdown on window close."""
        logger.info("Application shutting down...")
        self.scanner.stop()

        try:
            import keyboard
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass

        self.destroy()
