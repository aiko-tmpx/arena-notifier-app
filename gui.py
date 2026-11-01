"""Modern Single Page Application GUI for AikoArenaNotifier built with CustomTkinter.
Features dark theme, sidebar navigation, live diagnostics, settings, and multilingual guide.
"""

from __future__ import annotations

import datetime
import logging
import threading
from typing import Dict, List, Optional, Tuple

import customtkinter as ctk

from config import ConfigManager
from localization import get_supported_languages, t
from notifier import SoundNotifier, TelegramNotifier, format_queue_pop_message
from scanner import ScreenScanner, get_monitors

logger = logging.getLogger("AikoArenaNotifier.GUI")

# Palette constants
COLOR_BG = "#0f0f14"
COLOR_SIDEBAR = "#16161f"
COLOR_CARD = "#1c1c28"
COLOR_CARD_BORDER = "#2b2b3d"
COLOR_TEXT_PRIMARY = "#f4f4f6"
COLOR_TEXT_MUTED = "#9393a6"
COLOR_ACCENT_PURPLE = "#a330c9"
COLOR_ACCENT_HOVER = "#8824a8"
COLOR_SUCCESS_GREEN = "#10b981"
COLOR_SUCCESS_HOVER = "#059669"
COLOR_DANGER_RED = "#ef4444"
COLOR_DANGER_HOVER = "#dc2626"
COLOR_STATUS_IDLE = "#71717a"
COLOR_STATUS_SCANNING = "#10b981"


class MainWindow(ctk.CTk):
    """Main application window implementing the Single Page Application (SPA) architecture."""

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

        # Window configuration
        self.title("AikoArenaNotifier")
        self.geometry("780x520")
        self.minsize(780, 520)
        self.maxsize(780, 520)
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Monitored display list
        self.monitors = get_monitors()

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

        # Build UI layout
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()

        # Bind initial global hotkey
        self._register_global_hotkey(self._current_hotkey)

        # Select default view (Dashboard)
        self.switch_view("dashboard")

        # Initial log
        lang = self.cfg.get("language", "en")
        self.log_event(t("log_app_ready", lang))

        # Sample initial pixel for preview swatch
        self.after(200, self._sample_initial_pixel)

    def _setup_layout(self) -> None:
        """Configures root 2-column grid layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=210)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)               # Right Viewport

        # Sidebar container
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0,
            fg_color=COLOR_SIDEBAR,
            border_width=0,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        # Content viewport container
        self.viewport_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLOR_BG,
            border_width=0,
        )
        self.viewport_frame.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.viewport_frame.grid_rowconfigure(0, weight=1)
        self.viewport_frame.grid_columnconfigure(0, weight=1)

    def _setup_sidebar(self) -> None:
        """Constructs left navigation sidebar with header, tabs, and persistent status footer."""
        lang = self.cfg.get("language", "en")

        # 1. App Title / Logo
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(18, 20))

        title_label = ctk.CTkLabel(
            logo_frame,
            text="AikoArenaNotifier",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        version_label = ctk.CTkLabel(
            logo_frame,
            text=f"{t('app_version', lang)} • PvP Companion",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_ACCENT_PURPLE,
        )
        version_label.pack(anchor="w")

        # 2. Navigation buttons
        nav_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_container.pack(fill="x", padx=12, pady=0)

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        tabs = [
            ("dashboard", "📊 " + t("tab_dashboard", lang)),
            ("settings", "⚙️ " + t("tab_settings", lang)),
            ("guide", "📖 " + t("tab_guide", lang)),
        ]

        for tab_id, tab_label in tabs:
            btn = ctk.CTkButton(
                nav_container,
                text=tab_label,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color=COLOR_CARD,
                height=38,
                corner_radius=8,
                command=lambda tid=tab_id: self.switch_view(tid),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[tab_id] = btn

        # Spacer to push footer to bottom
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # 3. Persistent Status Indicator Footer
        footer_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        footer_frame.pack(fill="x", padx=12, pady=16)

        status_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=(10, 4))

        self.lbl_status_dot = ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_STATUS_IDLE,
            width=16,
        )
        self.lbl_status_dot.pack(side="left")

        self.lbl_status_text = ctk.CTkLabel(
            status_row,
            text=t("status_idle", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_STATUS_IDLE,
        )
        self.lbl_status_text.pack(side="left", padx=4)

        self.lbl_footer_hotkey = ctk.CTkLabel(
            footer_frame,
            text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_footer_hotkey.pack(anchor="w", padx=12, pady=(0, 10))

    def _setup_views(self) -> None:
        """Instantiates the three SPA views inside the content viewport."""
        self.views: Dict[str, ctk.CTkFrame] = {
            "dashboard": self._create_dashboard_view(),
            "settings": self._create_settings_view(),
            "guide": self._create_guide_view(),
        }

    # =========================================================================
    # VIEW 1: DASHBOARD
    # =========================================================================
    def _create_dashboard_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self.viewport_frame, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        lang = self.cfg.get("language", "en")

        # Hero Status Banner
        self.hero_frame = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        self.hero_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        hero_inner = ctk.CTkFrame(self.hero_frame, fg_color="transparent")
        hero_inner.pack(fill="x", padx=16, pady=12)

        self.lbl_hero_title = ctk.CTkLabel(
            hero_inner,
            text=t("hero_idle_title", lang),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_hero_title.pack(anchor="w")

        self.lbl_hero_subtitle = ctk.CTkLabel(
            hero_inner,
            text=t("hero_idle_subtitle", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_hero_subtitle.pack(anchor="w", pady=(2, 0))

        # Big Action Toggle Button
        btn_text = t("btn_start_scan", lang, hotkey=self._current_hotkey)
        self.btn_toggle_scan = ctk.CTkButton(
            view,
            text=btn_text,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=COLOR_SUCCESS_GREEN,
            hover_color=COLOR_SUCCESS_HOVER,
            text_color="#ffffff",
            height=44,
            corner_radius=8,
            command=self.toggle_scanning,
        )
        self.btn_toggle_scan.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Diagnostics Panel Card
        diag_card = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        diag_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        diag_inner = ctk.CTkFrame(diag_card, fg_color="transparent")
        diag_inner.pack(fill="x", padx=16, pady=10)

        # Diag Left column: Monitor & Sample point
        col_left = ctk.CTkFrame(diag_inner, fg_color="transparent")
        col_left.pack(side="left", fill="both", expand=True)

        current_mon = self._get_current_monitor_label()
        self.lbl_diag_monitor = ctk.CTkLabel(
            col_left,
            text=f"{t('diag_monitor', lang)} {current_mon}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_diag_monitor.pack(anchor="w")

        lbl_diag_coords = ctk.CTkLabel(
            col_left,
            text=t("diag_pixel", lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        lbl_diag_coords.pack(anchor="w", pady=(2, 0))

        # Diag Right column: Live RGB & Swatch
        col_right = ctk.CTkFrame(diag_inner, fg_color="transparent")
        col_right.pack(side="right")

        self.lbl_diag_rgb = ctk.CTkLabel(
            col_right,
            text=f"{t('diag_current_rgb', lang)} (0, 0, 0)",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_diag_rgb.pack(side="left", padx=(0, 10))

        self.swatch_preview = ctk.CTkFrame(
            col_right,
            width=28,
            height=28,
            corner_radius=6,
            fg_color="#000000",
            border_width=1,
            border_color="#444455",
        )
        self.swatch_preview.pack(side="left")

        # Activity Log Card
        log_card = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        log_card.grid(row=3, column=0, sticky="nsew")
        view.grid_rowconfigure(3, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=14, pady=(8, 4))

        lbl_log_title = ctk.CTkLabel(
            log_header,
            text=t("log_title", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_log_title.pack(side="left")

        btn_clear_log = ctk.CTkButton(
            log_header,
            text=t("btn_clear_log", lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="transparent",
            text_color=COLOR_TEXT_MUTED,
            hover_color=COLOR_CARD_BORDER,
            height=24,
            width=70,
            corner_radius=5,
            command=self.clear_log,
        )
        btn_clear_log.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            log_card,
            fg_color="#121219",
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=6,
            activate_scrollbars=True,
        )
        self.log_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.log_textbox.configure(state="disabled")

        return view

    # =========================================================================
    # VIEW 2: SETTINGS
    # =========================================================================
    def _create_settings_view(self) -> ctk.CTkFrame:
        view = ctk.CTkScrollableFrame(
            self.viewport_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        view.grid_columnconfigure(0, weight=1)
        lang = self.cfg.get("language", "en")

        # Settings Card Container
        card = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        card.pack(fill="both", expand=True, padx=2, pady=2)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        # 1. Telegram Bot Token
        lbl_token = ctk.CTkLabel(
            inner,
            text=t("settings_tg_token_label", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_token.pack(anchor="w")

        token_row = ctk.CTkFrame(inner, fg_color="transparent")
        token_row.pack(fill="x", pady=(4, 12))

        self.entry_token = ctk.CTkEntry(
            token_row,
            show="*",
            placeholder_text=t("settings_tg_token_placeholder", lang),
            font=ctk.CTkFont(family="Consolas", size=12),
            height=34,
            corner_radius=6,
        )
        self.entry_token.pack(side="left", fill="x", expand=True)
        if self.cfg.get("telegram_bot_token"):
            self.entry_token.insert(0, self.cfg["telegram_bot_token"])

        self._token_visible = False
        self.btn_toggle_token = ctk.CTkButton(
            token_row,
            text="👁️",
            width=36,
            height=34,
            corner_radius=6,
            fg_color=COLOR_CARD_BORDER,
            hover_color="#3c3c52",
            command=self._toggle_token_visibility,
        )
        self.btn_toggle_token.pack(side="left", padx=(6, 0))

        # 2. Telegram Chat ID
        lbl_chat_id = ctk.CTkLabel(
            inner,
            text=t("settings_tg_chat_id_label", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_chat_id.pack(anchor="w")

        self.entry_chat_id = ctk.CTkEntry(
            inner,
            placeholder_text=t("settings_tg_chat_id_placeholder", lang),
            font=ctk.CTkFont(family="Consolas", size=12),
            height=34,
            corner_radius=6,
        )
        self.entry_chat_id.pack(fill="x", pady=(4, 12))
        if self.cfg.get("telegram_chat_id"):
            self.entry_chat_id.insert(0, str(self.cfg["telegram_chat_id"]))

        # 3. Target Display Selector
        lbl_display = ctk.CTkLabel(
            inner,
            text=t("settings_display_label", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_display.pack(anchor="w")

        monitor_labels = [m["label"] for m in self.monitors]
        selected_mon_idx = self.cfg.get("selected_display_index", 0)
        default_mon_label = (
            monitor_labels[selected_mon_idx]
            if 0 <= selected_mon_idx < len(monitor_labels)
            else monitor_labels[0]
        )

        self.opt_display = ctk.CTkOptionMenu(
            inner,
            values=monitor_labels,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34,
            corner_radius=6,
            fg_color=COLOR_CARD_BORDER,
            button_color="#3c3c52",
            button_hover_color=COLOR_ACCENT_PURPLE,
        )
        self.opt_display.set(default_mon_label)
        self.opt_display.pack(fill="x", pady=(4, 12))

        # 4. Hotkey Selector
        lbl_hotkey = ctk.CTkLabel(
            inner,
            text=t("settings_hotkey_label", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_hotkey.pack(anchor="w")

        hotkey_options = ["F8", "F9", "F10", "F11", "F12"]
        current_hk = self.cfg.get("hotkey", "F9")
        if current_hk not in hotkey_options:
            hotkey_options.append(current_hk)

        self.opt_hotkey = ctk.CTkOptionMenu(
            inner,
            values=hotkey_options,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34,
            corner_radius=6,
            fg_color=COLOR_CARD_BORDER,
            button_color="#3c3c52",
            button_hover_color=COLOR_ACCENT_PURPLE,
        )
        self.opt_hotkey.set(current_hk)
        self.opt_hotkey.pack(fill="x", pady=(4, 14))

        # 5. Sound Checkbox
        self.chk_sound = ctk.CTkCheckBox(
            inner,
            text=t("settings_sound_label", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXT_PRIMARY,
            fg_color=COLOR_ACCENT_PURPLE,
            hover_color=COLOR_ACCENT_HOVER,
        )
        if self.cfg.get("sound_enabled", True):
            self.chk_sound.select()
        else:
            self.chk_sound.deselect()
        self.chk_sound.pack(anchor="w", pady=(0, 16))

        # 6. Action Buttons & Feedback Status
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 8))

        self.btn_test_tg = ctk.CTkButton(
            btn_row,
            text="🔔 " + t("settings_test_tg_btn", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLOR_CARD_BORDER,
            hover_color="#3c3c52",
            height=36,
            corner_radius=6,
            command=self._on_test_telegram,
        )
        self.btn_test_tg.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_save_settings = ctk.CTkButton(
            btn_row,
            text="💾 " + t("settings_save_btn", lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLOR_ACCENT_PURPLE,
            hover_color=COLOR_ACCENT_HOVER,
            height=36,
            corner_radius=6,
            command=self._on_save_settings,
        )
        self.btn_save_settings.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Inline Feedback Status Label
        self.lbl_settings_status = ctk.CTkLabel(
            inner,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_settings_status.pack(anchor="w", pady=(4, 0))

        return view

    # =========================================================================
    # VIEW 3: GUIDE / HELP
    # =========================================================================
    def _create_guide_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self.viewport_frame, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(1, weight=1)
        lang = self.cfg.get("language", "en")

        # Top Bar: Title & Language Selector
        top_bar = ctk.CTkFrame(view, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        lbl_guide_title = ctk.CTkLabel(
            top_bar,
            text=t("guide_title", lang),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_guide_title.pack(side="left")

        # Language Selector Segmented Button
        current_lang_str = "Русский" if lang == "ru" else "English"
        self.seg_lang = ctk.CTkSegmentedButton(
            top_bar,
            values=["English", "Русский"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            selected_color=COLOR_ACCENT_PURPLE,
            selected_hover_color=COLOR_ACCENT_HOVER,
            command=self._on_language_change,
        )
        self.seg_lang.set(current_lang_str)
        self.seg_lang.pack(side="right")

        # Scrollable Steps Container
        scroll_steps = ctk.CTkScrollableFrame(
            view,
            fg_color="transparent",
            corner_radius=0,
        )
        scroll_steps.grid(row=1, column=0, sticky="nsew")
        scroll_steps.grid_columnconfigure(0, weight=1)

        self.guide_step_labels: List[Tuple[ctk.CTkLabel, ctk.CTkLabel]] = []

        steps = [
            ("guide_step1_title", "guide_step1_body"),
            ("guide_step2_title", "guide_step2_body"),
            ("guide_step3_title", "guide_step3_body"),
            ("guide_step4_title", "guide_step4_body"),
        ]

        for step_idx, (title_key, body_key) in enumerate(steps):
            step_card = ctk.CTkFrame(
                scroll_steps,
                fg_color=COLOR_CARD,
                corner_radius=8,
                border_width=1,
                border_color=COLOR_CARD_BORDER,
            )
            step_card.pack(fill="x", pady=6)

            card_inner = ctk.CTkFrame(step_card, fg_color="transparent")
            card_inner.pack(fill="x", padx=14, pady=10)

            title_lbl = ctk.CTkLabel(
                card_inner,
                text=t(title_key, lang),
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLOR_ACCENT_PURPLE,
            )
            title_lbl.pack(anchor="w")

            body_lbl = ctk.CTkLabel(
                card_inner,
                text=t(body_key, lang),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLOR_TEXT_PRIMARY,
                justify="left",
                wraplength=480,
            )
            body_lbl.pack(anchor="w", pady=(4, 0))

            self.guide_step_labels.append((title_lbl, body_lbl))

        return view

    # =========================================================================
    # SPA NAVIGATION CONTROLLER
    # =========================================================================
    def switch_view(self, target_view: str) -> None:
        """Hides current view and shows selected target view."""
        for name, frame in self.views.items():
            if name == target_view:
                frame.grid(row=0, column=0, sticky="nsew")
                # Highlight active button
                self.nav_buttons[name].configure(
                    fg_color=COLOR_CARD,
                    text_color=COLOR_TEXT_PRIMARY,
                )
            else:
                frame.grid_forget()
                # De-highlight inactive buttons
                self.nav_buttons[name].configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_MUTED,
                )

    # =========================================================================
    # SCANNER & STATE CONTROLLER
    # =========================================================================
    def toggle_scanning(self) -> None:
        """Toggles screen scanner state between IDLE and SCANNING."""
        if self.scanner.is_scanning:
            self.stop_scanning()
        else:
            self.start_scanning()

    def start_scanning(self) -> None:
        """Arms scanner and transitions UI to SCANNING state."""
        lang = self.cfg.get("language", "en")
        mon_label = self._get_current_monitor_label()

        if self.scanner.start():
            self._update_ui_state(is_scanning=True)
            self.log_event(t("log_scanner_armed", lang, display=mon_label))

    def stop_scanning(self) -> None:
        """Disarms scanner and transitions UI to IDLE state."""
        lang = self.cfg.get("language", "en")
        self.scanner.stop()
        self._update_ui_state(is_scanning=False)
        self.log_event(t("log_scanner_stopped", lang))

    def _update_ui_state(self, is_scanning: bool) -> None:
        """Updates hero banners, buttons, and status indicator footer."""
        lang = self.cfg.get("language", "en")

        if is_scanning:
            # Running state
            self.lbl_status_dot.configure(text_color=COLOR_STATUS_SCANNING)
            self.lbl_status_text.configure(
                text=t("status_scanning", lang),
                text_color=COLOR_STATUS_SCANNING,
            )
            self.lbl_hero_title.configure(text=t("hero_scanning_title", lang))
            self.lbl_hero_subtitle.configure(text=t("hero_scanning_subtitle", lang))
            self.btn_toggle_scan.configure(
                text=t("btn_stop_scan", lang, hotkey=self._current_hotkey),
                fg_color=COLOR_DANGER_RED,
                hover_color=COLOR_DANGER_HOVER,
            )
        else:
            # Idle state
            self.lbl_status_dot.configure(text_color=COLOR_STATUS_IDLE)
            self.lbl_status_text.configure(
                text=t("status_idle", lang),
                text_color=COLOR_STATUS_IDLE,
            )
            self.lbl_hero_title.configure(text=t("hero_idle_title", lang))
            self.lbl_hero_subtitle.configure(text=t("hero_idle_subtitle", lang))
            self.btn_toggle_scan.configure(
                text=t("btn_start_scan", lang, hotkey=self._current_hotkey),
                fg_color=COLOR_SUCCESS_GREEN,
                hover_color=COLOR_SUCCESS_HOVER,
            )

    def _on_scanner_tick(self, rgb: Tuple[int, int, int]) -> None:
        """Receives live sampled RGB from background thread; marshals to GUI thread."""
        self.after(0, self._update_diagnostics_swatch, rgb)

    def _on_scanner_pop(self) -> None:
        """Invoked when pop marker is detected. Marshals to GUI thread for alerts."""
        self.after(0, self._handle_queue_pop)

    def _update_diagnostics_swatch(self, rgb: Tuple[int, int, int]) -> None:
        """Updates live RGB label and color swatch preview."""
        r, g, b = rgb
        lang = self.cfg.get("language", "en")
        self.lbl_diag_rgb.configure(text=f"{t('diag_current_rgb', lang)} ({r}, {g}, {b})")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.swatch_preview.configure(fg_color=hex_color)

    def _handle_queue_pop(self) -> None:
        """Handles queue pop event: audio alert, Telegram dispatch, and logging."""
        lang = self.cfg.get("language", "en")

        # 1. Update UI state (scanner has already set is_scanning = False)
        self._update_ui_state(is_scanning=False)
        self.log_event(t("log_pop_detected", lang))
        self.log_event(t("log_auto_stopped", lang))

        # 2. Local PC sound alert
        if self.cfg.get("sound_enabled", True):
            self.sound_notifier.play_pop_sound(enabled=True)
            self.log_event(t("log_sound_played", lang))

        # 3. Telegram push notification (asynchronous background worker)
        token = self.cfg.get("telegram_bot_token", "").strip()
        chat_id = self.cfg.get("telegram_chat_id", "").strip()

        if token and chat_id:
            self.log_event(t("log_telegram_sending", lang))

            def _send_worker():
                msg = format_queue_pop_message(lang)
                ok, err = self.telegram_notifier.send_message(token, chat_id, msg)
                self.after(0, self._on_telegram_result, ok, err)

            threading.Thread(target=_send_worker, daemon=True, name="TgSendThread").start()
        else:
            self.log_event(t("log_telegram_skipped", lang))

    def _on_telegram_result(self, ok: bool, err_msg: str) -> None:
        """Logs Telegram push notification outcome."""
        lang = self.cfg.get("language", "en")
        if ok:
            self.log_event(t("log_telegram_success", lang))
        else:
            self.log_event(t("log_telegram_error", lang, error=err_msg))

    # =========================================================================
    # SETTINGS ACTIONS
    # =========================================================================
    def _toggle_token_visibility(self) -> None:
        """Toggles Telegram bot token entry between masked and plaintext."""
        self._token_visible = not self._token_visible
        self.entry_token.configure(show="" if self._token_visible else "*")
        self.btn_toggle_token.configure(text="🔒" if self._token_visible else "👁️")

    def _on_test_telegram(self) -> None:
        """Executes Telegram connection test in background thread."""
        lang = self.cfg.get("language", "en")
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token:
            self.lbl_settings_status.configure(
                text=t("status_token_empty", lang),
                text_color=COLOR_DANGER_RED,
            )
            return

        if not chat_id:
            self.lbl_settings_status.configure(
                text=t("status_chat_id_empty", lang),
                text_color=COLOR_DANGER_RED,
            )
            return

        self.lbl_settings_status.configure(
            text=t("status_testing_connection", lang),
            text_color=COLOR_ACCENT_PURPLE,
        )
        self.btn_test_tg.configure(state="disabled")

        def _test_worker():
            ok, msg = self.telegram_notifier.test_connection(token, chat_id, lang)
            self.after(0, self._on_test_telegram_finished, ok, msg)

        threading.Thread(target=_test_worker, daemon=True, name="TgTestThread").start()

    def _on_test_telegram_finished(self, ok: bool, msg: str) -> None:
        """Handles completion of Telegram connection test."""
        lang = self.cfg.get("language", "en")
        self.btn_test_tg.configure(state="normal")

        if ok:
            self.lbl_settings_status.configure(
                text=f"{t('status_test_success', lang)} ({msg})",
                text_color=COLOR_SUCCESS_GREEN,
            )
        else:
            self.lbl_settings_status.configure(
                text=t("status_test_failed", lang, error=msg),
                text_color=COLOR_DANGER_RED,
            )

    def _on_save_settings(self) -> None:
        """Saves current settings inputs to config.json and updates runtime state."""
        lang = self.cfg.get("language", "en")
        new_token = self.entry_token.get().strip()
        new_chat_id = self.entry_chat_id.get().strip()
        new_hotkey = self.opt_hotkey.get().strip()
        new_sound = bool(self.chk_sound.get())

        # Resolve selected display index
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

            # Update hotkey binding if changed
            if new_hotkey != self._current_hotkey:
                self._register_global_hotkey(new_hotkey)

            # Update UI labels
            self.lbl_diag_monitor.configure(
                text=f"{t('diag_monitor', lang)} {self._get_current_monitor_label()}"
            )
            self.lbl_footer_hotkey.configure(
                text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}"
            )
            self._update_ui_state(is_scanning=self.scanner.is_scanning)

            self.lbl_settings_status.configure(
                text=t("status_saved_success", lang),
                text_color=COLOR_SUCCESS_GREEN,
            )
            self.log_event(t("log_settings_saved", lang))
        else:
            self.lbl_settings_status.configure(
                text=t("status_saved_failed", lang),
                text_color=COLOR_DANGER_RED,
            )

    # =========================================================================
    # GUIDE / LANGUAGE SELECTOR
    # =========================================================================
    def _on_language_change(self, selected_lang_name: str) -> None:
        """Switches guide and app language between English and Russian."""
        new_lang = "ru" if selected_lang_name == "Русский" else "en"
        self.cfg["language"] = new_lang
        self.config_manager.save_config({"language": new_lang})

        # Update guide card text
        steps = [
            ("guide_step1_title", "guide_step1_body"),
            ("guide_step2_title", "guide_step2_body"),
            ("guide_step3_title", "guide_step3_body"),
            ("guide_step4_title", "guide_step4_body"),
        ]
        for idx, (title_k, body_k) in enumerate(steps):
            t_lbl, b_lbl = self.guide_step_labels[idx]
            t_lbl.configure(text=t(title_k, new_lang))
            b_lbl.configure(text=t(body_k, new_lang))

        # Refresh all static labels in other views
        self._refresh_translations(new_lang)

    def _refresh_translations(self, lang: str) -> None:
        """Refreshes dynamic localized strings across tabs and footers."""
        self.nav_buttons["dashboard"].configure(text="📊 " + t("tab_dashboard", lang))
        self.nav_buttons["settings"].configure(text="⚙️ " + t("tab_settings", lang))
        self.nav_buttons["guide"].configure(text="📖 " + t("tab_guide", lang))

        self.lbl_footer_hotkey.configure(
            text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}"
        )
        self.lbl_diag_monitor.configure(
            text=f"{t('diag_monitor', lang)} {self._get_current_monitor_label()}"
        )

        self._update_ui_state(is_scanning=self.scanner.is_scanning)

    # =========================================================================
    # GLOBAL HOTKEY MANAGEMENT
    # =========================================================================
    def _register_global_hotkey(self, hotkey_str: str) -> None:
        """Safely binds global toggle hotkey using keyboard library."""
        lang = self.cfg.get("language", "en")
        try:
            import keyboard

            # Clean previous hook
            if self._hotkey_hook:
                try:
                    keyboard.remove_hotkey(self._hotkey_hook)
                except Exception:
                    pass

            self._hotkey_hook = keyboard.add_hotkey(
                hotkey_str,
                lambda: self.after(0, self.toggle_scanning),
            )
            self._current_hotkey = hotkey_str
            self.log_event(t("log_hotkey_bound", lang, hotkey=hotkey_str))
        except Exception as e:
            logger.warning(f"Could not register hotkey {hotkey_str}: {e}")
            self.log_event(t("log_hotkey_error", lang, hotkey=hotkey_str))

    # =========================================================================
    # HELPERS
    # =========================================================================
    def _sample_initial_pixel(self) -> None:
        """Performs initial sample to populate swatch."""
        try:
            rgb = self.scanner.sample_current_pixel()
            self._update_diagnostics_swatch(rgb)
        except Exception:
            pass

    def _get_current_monitor_label(self) -> str:
        """Returns readable label for currently selected monitor."""
        idx = self.scanner.display_index
        if 0 <= idx < len(self.monitors):
            return self.monitors[idx]["name"]
        return "Display 1"

    def log_event(self, message: str) -> None:
        """Appends timestamped message to the activity log textbox."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\n"

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", entry)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear_log(self) -> None:
        """Clears activity log textbox."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

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
