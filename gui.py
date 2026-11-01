"""Minimalist, refined Single Page Application GUI for AikoArenaNotifier.
Features cohesive dark slate palette, violet primary accents, Segoe UI typography,
typographic sidebar, and global language switcher in Settings.
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

# =============================================================================
# COHESIVE MINIMALIST COLOR PALETTE
# =============================================================================
COLOR_BG = "#0F1117"             # Deep slate dark surface
COLOR_SIDEBAR = "#141721"        # Elevated sidebar surface
COLOR_CARD = "#1D212C"           # Elevated card surface
COLOR_CARD_BORDER = "#282F3E"    # Subtle card border
COLOR_SURFACE_ALT = "#161922"    # Input & badge surface
COLOR_INPUT_BORDER = "#2B3345"   # Input field border
COLOR_NAV_ACTIVE = "#252B3B"     # Active navigation item background
COLOR_ACCENT = "#7C3AED"         # Violet / Purple primary accent
COLOR_ACCENT_HOVER = "#6D28D9"   # Darker violet hover
COLOR_ACCENT_BAR = "#8B5CF6"     # Left accent indicator bar
COLOR_TEXT_PRIMARY = "#F3F4F6"   # Crisp clean off-white
COLOR_TEXT_MUTED = "#94A3B8"     # Neutral secondary text
COLOR_TEXT_DIM = "#6B7280"       # Dim timestamp & metadata text
COLOR_STATUS_ACTIVE = "#10B981"  # Emerald green (Scanning)
COLOR_STATUS_IDLE = "#6B7280"    # Slate grey (Idle)
COLOR_STATUS_ALERT = "#EC4899"   # Accent magenta (Triggered)
COLOR_DANGER = "#EF4444"         # Stop action red
COLOR_DANGER_HOVER = "#DC2626"


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

        # Window geometry: increased to 860x540 for generous breathing room
        self.title("AikoArenaNotifier")
        self.geometry("860x540")
        self.minsize(860, 540)
        self.maxsize(860, 540)
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Monitored display list
        self.monitors = get_monitors()

        # Typography Scale (Native Windows Segoe UI)
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

        # In-memory recent events buffer (keeps last 5 events)
        self._recent_events: List[str] = []

        # Build UI layout
        self._setup_layout()
        self._setup_sidebar()
        self._setup_views()

        # Bind initial global hotkey
        self._register_global_hotkey(self._current_hotkey)

        # Select default view (Dashboard)
        self.switch_view("dashboard")

        # Initial ready event
        lang = self.cfg.get("language", "en")
        self.log_event(t("log_app_ready", lang))

    def _init_typography(self) -> None:
        """Defines standardized typography scale using Segoe UI and Consolas."""
        self.font_header = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.font_subheader = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.font_body = ctk.CTkFont(family="Segoe UI", size=13)
        self.font_body_bold = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_meta = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_meta_bold = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        self.font_mono = ctk.CTkFont(family="Consolas", size=11)

    def _setup_layout(self) -> None:
        """Configures root 2-column grid layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=210)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)               # Right Viewport

        # Left Sidebar Container
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0,
            fg_color=COLOR_SIDEBAR,
            border_width=0,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        # Right Content Viewport Container
        self.viewport_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLOR_BG,
            border_width=0,
        )
        self.viewport_frame.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.viewport_frame.grid_rowconfigure(0, weight=1)
        self.viewport_frame.grid_columnconfigure(0, weight=1)

    def _setup_sidebar(self) -> None:
        """Constructs left navigation sidebar with clean typographic navigation buttons."""
        lang = self.cfg.get("language", "en")

        # 1. Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(22, 26))

        title_label = ctk.CTkLabel(
            brand_frame,
            text="AikoArenaNotifier",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        version_label = ctk.CTkLabel(
            brand_frame,
            text=f"{t('app_version', lang)} • PvP Companion",
            font=self.font_meta_bold,
            text_color=COLOR_ACCENT_BAR,
        )
        version_label.pack(anchor="w", pady=(2, 0))

        # 2. Typographic Navigation items (No emojis / broken glyphs)
        nav_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_container.pack(fill="x", padx=12, pady=0)

        self.nav_item_frames: Dict[str, ctk.CTkFrame] = {}
        self.nav_accent_bars: Dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        tabs = [
            ("dashboard", t("tab_dashboard", lang)),
            ("settings", t("tab_settings", lang)),
            ("guide", t("tab_guide", lang)),
        ]

        for tab_id, tab_label in tabs:
            item_frame = ctk.CTkFrame(
                nav_container,
                height=38,
                corner_radius=6,
                fg_color="transparent",
            )
            item_frame.pack(fill="x", pady=2)
            item_frame.pack_propagate(False)

            accent_bar = ctk.CTkFrame(
                item_frame,
                width=3,
                corner_radius=2,
                fg_color="transparent",
            )
            accent_bar.pack(side="left", fill="y", padx=(2, 8), pady=4)

            btn = ctk.CTkButton(
                item_frame,
                text=tab_label,
                anchor="w",
                font=self.font_body,
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color=COLOR_CARD,
                height=38,
                corner_radius=6,
                command=lambda tid=tab_id: self.switch_view(tid),
            )
            btn.pack(side="left", fill="both", expand=True)

            self.nav_item_frames[tab_id] = item_frame
            self.nav_accent_bars[tab_id] = accent_bar
            self.nav_buttons[tab_id] = btn

        # Spacer
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # 3. Persistent Status Indicator Footer
        footer_card = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        footer_card.pack(fill="x", padx=12, pady=18)

        status_row = ctk.CTkFrame(footer_card, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=(10, 4))

        self.lbl_status_dot = ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_STATUS_IDLE,
            width=14,
        )
        self.lbl_status_dot.pack(side="left")

        self.lbl_status_text = ctk.CTkLabel(
            status_row,
            text=t("status_idle", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_status_text.pack(side="left", padx=4)

        self.lbl_footer_hotkey = ctk.CTkLabel(
            footer_card,
            text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}",
            font=self.font_meta,
            text_color=COLOR_TEXT_DIM,
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

        # 1. Compact Status Banner Card
        self.hero_frame = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        self.hero_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        hero_inner = ctk.CTkFrame(self.hero_frame, fg_color="transparent")
        hero_inner.pack(fill="x", padx=18, pady=14)

        title_row = ctk.CTkFrame(hero_inner, fg_color="transparent")
        title_row.pack(fill="x")

        self.lbl_hero_dot = ctk.CTkLabel(
            title_row,
            text="●",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_STATUS_IDLE,
            width=16,
        )
        self.lbl_hero_dot.pack(side="left")

        self.lbl_hero_title = ctk.CTkLabel(
            title_row,
            text=t("hero_idle_title", lang),
            font=self.font_subheader,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_hero_title.pack(side="left", padx=6)

        self.lbl_hero_subtitle = ctk.CTkLabel(
            hero_inner,
            text=t("hero_idle_subtitle", lang),
            font=self.font_meta,
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_hero_subtitle.pack(anchor="w", padx=(22, 0), pady=(3, 0))

        # 2. Sleek Action Toggle Button
        btn_text = t("btn_start_scan", lang, hotkey=self._current_hotkey)
        self.btn_toggle_scan = ctk.CTkButton(
            view,
            text=btn_text,
            font=self.font_body_bold,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            height=42,
            corner_radius=8,
            command=self.toggle_scanning,
        )
        self.btn_toggle_scan.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # 3. Clean Metadata Line
        meta_card = ctk.CTkFrame(
            view,
            fg_color=COLOR_SURFACE_ALT,
            corner_radius=6,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        meta_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        meta_inner = ctk.CTkFrame(meta_card, fg_color="transparent")
        meta_inner.pack(fill="x", padx=14, pady=8)

        self.lbl_metadata = ctk.CTkLabel(
            meta_inner,
            text=self._get_metadata_summary_text(),
            font=self.font_meta,
            text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_metadata.pack(anchor="w")

        # 4. Sleek Recent Activity Card
        activity_card = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        activity_card.grid(row=3, column=0, sticky="nsew")
        view.grid_rowconfigure(3, weight=1)

        act_header = ctk.CTkFrame(activity_card, fg_color="transparent")
        act_header.pack(fill="x", padx=16, pady=(12, 6))

        lbl_act_title = ctk.CTkLabel(
            act_header,
            text=t("recent_activity_title", lang),
            font=self.font_body_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_act_title.pack(side="left")

        btn_clear = ctk.CTkButton(
            act_header,
            text=t("btn_clear_log", lang),
            font=self.font_meta,
            fg_color="transparent",
            text_color=COLOR_TEXT_DIM,
            hover_color=COLOR_CARD_BORDER,
            height=22,
            width=50,
            corner_radius=4,
            command=self.clear_log,
        )
        btn_clear.pack(side="right")

        # Compact activity display box with generous inner margins
        self.log_textbox = ctk.CTkTextbox(
            activity_card,
            fg_color=COLOR_SURFACE_ALT,
            text_color=COLOR_TEXT_PRIMARY,
            font=self.font_mono,
            corner_radius=6,
            activate_scrollbars=False,
            border_width=0,
        )
        self.log_textbox.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.log_textbox.configure(state="disabled")

        return view

    # =========================================================================
    # VIEW 2: SETTINGS (FEATURING GLOBAL LANGUAGE SWITCHER)
    # =========================================================================
    def _create_settings_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self.viewport_frame, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        lang = self.cfg.get("language", "en")

        card = ctk.CTkFrame(
            view,
            fg_color=COLOR_CARD,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
        )
        card.pack(fill="both", expand=True, padx=0, pady=0)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. Global Application Language Switcher
        self.lbl_lang_setting = ctk.CTkLabel(
            inner,
            text=t("settings_lang_label", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_lang_setting.pack(anchor="w")

        current_lang_str = "Русский" if lang == "ru" else "English"
        self.seg_lang = ctk.CTkSegmentedButton(
            inner,
            values=["English", "Русский"],
            font=self.font_body,
            height=32,
            corner_radius=6,
            fg_color=COLOR_SURFACE_ALT,
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_ACCENT_HOVER,
            command=self._on_language_change,
        )
        self.seg_lang.set(current_lang_str)
        self.seg_lang.pack(anchor="w", pady=(3, 10))

        # 2. Telegram Bot Token
        self.lbl_token = ctk.CTkLabel(
            inner,
            text=t("settings_tg_token_label", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_token.pack(anchor="w")

        token_row = ctk.CTkFrame(inner, fg_color="transparent")
        token_row.pack(fill="x", pady=(3, 8))

        self.entry_token = ctk.CTkEntry(
            token_row,
            show="*",
            placeholder_text=t("settings_tg_token_placeholder", lang),
            font=self.font_mono,
            height=32,
            corner_radius=6,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_token.pack(side="left", fill="x", expand=True)
        if self.cfg.get("telegram_bot_token"):
            self.entry_token.insert(0, self.cfg["telegram_bot_token"])

        self._token_visible = False
        self.btn_toggle_token = ctk.CTkButton(
            token_row,
            text="👁",
            width=34,
            height=32,
            corner_radius=6,
            fg_color=COLOR_NAV_ACTIVE,
            hover_color=COLOR_CARD_BORDER,
            command=self._toggle_token_visibility,
        )
        self.btn_toggle_token.pack(side="left", padx=(6, 0))

        # 3. Telegram Chat ID
        self.lbl_chat_id = ctk.CTkLabel(
            inner,
            text=t("settings_tg_chat_id_label", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_chat_id.pack(anchor="w")

        self.entry_chat_id = ctk.CTkEntry(
            inner,
            placeholder_text=t("settings_tg_chat_id_placeholder", lang),
            font=self.font_mono,
            height=32,
            corner_radius=6,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_chat_id.pack(fill="x", pady=(3, 8))
        if self.cfg.get("telegram_chat_id"):
            self.entry_chat_id.insert(0, str(self.cfg["telegram_chat_id"]))

        # 4. Target Game Display Selector
        self.lbl_display = ctk.CTkLabel(
            inner,
            text=t("settings_display_label", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_display.pack(anchor="w")

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
            font=self.font_body,
            height=32,
            corner_radius=6,
            fg_color=COLOR_SURFACE_ALT,
            button_color=COLOR_NAV_ACTIVE,
            button_hover_color=COLOR_ACCENT,
        )
        self.opt_display.set(default_mon_label)
        self.opt_display.pack(fill="x", pady=(3, 8))

        # 5. Hotkey Selector
        self.lbl_hotkey = ctk.CTkLabel(
            inner,
            text=t("settings_hotkey_label", lang),
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_hotkey.pack(anchor="w")

        hotkey_options = ["F8", "F9", "F10", "F11", "F12"]
        current_hk = self.cfg.get("hotkey", "F9")
        if current_hk not in hotkey_options:
            hotkey_options.append(current_hk)

        self.opt_hotkey = ctk.CTkOptionMenu(
            inner,
            values=hotkey_options,
            font=self.font_body,
            height=32,
            corner_radius=6,
            fg_color=COLOR_SURFACE_ALT,
            button_color=COLOR_NAV_ACTIVE,
            button_hover_color=COLOR_ACCENT,
        )
        self.opt_hotkey.set(current_hk)
        self.opt_hotkey.pack(fill="x", pady=(3, 10))

        # 6. Audio Alert Checkbox
        self.chk_sound = ctk.CTkCheckBox(
            inner,
            text=t("settings_sound_label", lang),
            font=self.font_body,
            text_color=COLOR_TEXT_PRIMARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            corner_radius=4,
        )
        if self.cfg.get("sound_enabled", True):
            self.chk_sound.select()
        else:
            self.chk_sound.deselect()
        self.chk_sound.pack(anchor="w", pady=(0, 14))

        # 7. Action Row
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 6))

        self.btn_test_tg = ctk.CTkButton(
            btn_row,
            text=t("settings_test_tg_btn", lang),
            font=self.font_body_bold,
            fg_color=COLOR_NAV_ACTIVE,
            hover_color="#2F374A",
            height=36,
            corner_radius=6,
            command=self._on_test_telegram,
        )
        self.btn_test_tg.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_save_settings = ctk.CTkButton(
            btn_row,
            text=t("settings_save_btn", lang),
            font=self.font_body_bold,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            height=36,
            corner_radius=6,
            command=self._on_save_settings,
        )
        self.btn_save_settings.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Fixed-height Status Feedback (Never shifts layout elements)
        feedback_container = ctk.CTkFrame(inner, height=20, fg_color="transparent")
        feedback_container.pack(fill="x", pady=(2, 0))
        feedback_container.pack_propagate(False)

        self.lbl_settings_status = ctk.CTkLabel(
            feedback_container,
            text="",
            font=self.font_meta_bold,
            text_color=COLOR_TEXT_DIM,
            anchor="w",
        )
        self.lbl_settings_status.pack(fill="both", expand=True)

        return view

    # =========================================================================
    # VIEW 3: GUIDE & HELP (CLEAN STRUCTURED CARDS)
    # =========================================================================
    def _create_guide_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self.viewport_frame, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(1, weight=1)
        lang = self.cfg.get("language", "en")

        # Top Bar: Clean Title
        top_bar = ctk.CTkFrame(view, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.lbl_guide_title = ctk.CTkLabel(
            top_bar,
            text=t("tab_guide", lang),
            font=self.font_subheader,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_guide_title.pack(side="left")

        # Scrollable Step Cards
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
            step_card.pack(fill="x", pady=5)

            card_inner = ctk.CTkFrame(step_card, fg_color="transparent")
            card_inner.pack(fill="x", padx=16, pady=12)

            title_lbl = ctk.CTkLabel(
                card_inner,
                text=t(title_key, lang),
                font=self.font_body_bold,
                text_color=COLOR_ACCENT_BAR,
            )
            title_lbl.pack(anchor="w")

            body_lbl = ctk.CTkLabel(
                card_inner,
                text=t(body_key, lang),
                font=self.font_body,
                text_color=COLOR_TEXT_PRIMARY,
                justify="left",
                wraplength=560,
            )
            body_lbl.pack(anchor="w", pady=(4, 0))

            self.guide_step_labels.append((title_lbl, body_lbl))

        return view

    # =========================================================================
    # SPA NAVIGATION CONTROLLER
    # =========================================================================
    def switch_view(self, target_view: str) -> None:
        """Hides current view and shows selected target view with active indicator."""
        for name, frame in self.views.items():
            if name == target_view:
                frame.grid(row=0, column=0, sticky="nsew")
                # Highlight active navigation item with solid fill and 3px left bar
                self.nav_item_frames[name].configure(fg_color=COLOR_NAV_ACTIVE)
                self.nav_accent_bars[name].configure(fg_color=COLOR_ACCENT_BAR)
                self.nav_buttons[name].configure(
                    text_color=COLOR_TEXT_PRIMARY,
                    font=self.font_body_bold,
                )
            else:
                frame.grid_forget()
                # De-highlight inactive items
                self.nav_item_frames[name].configure(fg_color="transparent")
                self.nav_accent_bars[name].configure(fg_color="transparent")
                self.nav_buttons[name].configure(
                    text_color=COLOR_TEXT_MUTED,
                    font=self.font_body,
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
        """Updates compact hero banner, button styling, and sidebar status footer."""
        lang = self.cfg.get("language", "en")

        if is_scanning:
            # Active Scanning state
            self.lbl_status_dot.configure(text_color=COLOR_STATUS_ACTIVE)
            self.lbl_status_text.configure(
                text=t("status_scanning", lang),
                text_color=COLOR_STATUS_ACTIVE,
            )
            self.lbl_hero_dot.configure(text_color=COLOR_STATUS_ACTIVE)
            self.lbl_hero_title.configure(text=t("hero_scanning_title", lang))
            self.lbl_hero_subtitle.configure(text=t("hero_scanning_subtitle", lang))
            self.btn_toggle_scan.configure(
                text=t("btn_stop_scan", lang, hotkey=self._current_hotkey),
                fg_color=COLOR_DANGER,
                hover_color=COLOR_DANGER_HOVER,
            )
        else:
            # Idle Paused state
            self.lbl_status_dot.configure(text_color=COLOR_STATUS_IDLE)
            self.lbl_status_text.configure(
                text=t("status_idle", lang),
                text_color=COLOR_TEXT_MUTED,
            )
            self.lbl_hero_dot.configure(text_color=COLOR_STATUS_IDLE)
            self.lbl_hero_title.configure(text=t("hero_idle_title", lang))
            self.lbl_hero_subtitle.configure(text=t("hero_idle_subtitle", lang))
            self.btn_toggle_scan.configure(
                text=t("btn_start_scan", lang, hotkey=self._current_hotkey),
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_HOVER,
            )

        # Update metadata line
        self.lbl_metadata.configure(text=self._get_metadata_summary_text())

    def _on_scanner_tick(self, rgb: Tuple[int, int, int]) -> None:
        """Background tick hook (no debug clutter in production view)."""
        pass

    def _on_scanner_pop(self) -> None:
        """Invoked when pop marker is detected. Marshals to GUI thread for alerts."""
        self.after(0, self._handle_queue_pop)

    def _handle_queue_pop(self) -> None:
        """Handles queue pop event: audio alert, Telegram dispatch, and logging."""
        lang = self.cfg.get("language", "en")

        # 1. Update UI state (scanner auto-stops)
        self._update_ui_state(is_scanning=False)
        self.log_event(t("log_pop_detected", lang))
        self.log_event(t("log_auto_stopped", lang))

        # 2. Local PC sound alert
        if self.cfg.get("sound_enabled", True):
            self.sound_notifier.play_pop_sound(enabled=True)
            self.log_event(t("log_sound_played", lang))

        # 3. Telegram push notification (daemon thread)
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
        self.btn_toggle_token.configure(text="🔒" if self._token_visible else "👁")

    def _on_test_telegram(self) -> None:
        """Executes Telegram connection test in background thread."""
        lang = self.cfg.get("language", "en")
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token:
            self.lbl_settings_status.configure(
                text=t("status_token_empty", lang),
                text_color=COLOR_DANGER,
            )
            return

        if not chat_id:
            self.lbl_settings_status.configure(
                text=t("status_chat_id_empty", lang),
                text_color=COLOR_DANGER,
            )
            return

        self.lbl_settings_status.configure(
            text=t("status_testing_connection", lang),
            text_color=COLOR_ACCENT_BAR,
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
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_settings_status.configure(
                text=t("status_test_failed", lang, error=msg),
                text_color=COLOR_DANGER,
            )

    def _on_save_settings(self) -> None:
        """Saves current settings inputs to config.json and updates runtime state."""
        lang = self.cfg.get("language", "en")
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

            self.lbl_footer_hotkey.configure(
                text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}"
            )
            self._update_ui_state(is_scanning=self.scanner.is_scanning)

            self.lbl_settings_status.configure(
                text=t("status_saved_success", lang),
                text_color=COLOR_STATUS_ACTIVE,
            )
            self.log_event(t("log_settings_saved", lang))
        else:
            self.lbl_settings_status.configure(
                text=t("status_saved_failed", lang),
                text_color=COLOR_DANGER,
            )

    # =========================================================================
    # GLOBAL LANGUAGE CONTROLLER
    # =========================================================================
    def _on_language_change(self, selected_lang_name: str) -> None:
        """Switches global language between English and Russian."""
        new_lang = "ru" if selected_lang_name == "Русский" else "en"
        self.cfg["language"] = new_lang
        self.config_manager.save_config({"language": new_lang})

        # Update Guide Cards text
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

        self._refresh_translations(new_lang)

    def _refresh_translations(self, lang: str) -> None:
        """Refreshes dynamic localized strings across tabs, settings labels, and footers."""
        # Navigation tabs
        self.nav_buttons["dashboard"].configure(text=t("tab_dashboard", lang))
        self.nav_buttons["settings"].configure(text=t("tab_settings", lang))
        self.nav_buttons["guide"].configure(text=t("tab_guide", lang))

        # Footer
        self.lbl_footer_hotkey.configure(
            text=f"{t('footer_hotkey_prefix', lang)} {self._current_hotkey}"
        )

        # Settings labels
        self.lbl_lang_setting.configure(text=t("settings_lang_label", lang))
        self.lbl_token.configure(text=t("settings_tg_token_label", lang))
        self.lbl_chat_id.configure(text=t("settings_tg_chat_id_label", lang))
        self.lbl_display.configure(text=t("settings_display_label", lang))
        self.lbl_hotkey.configure(text=t("settings_hotkey_label", lang))
        self.chk_sound.configure(text=t("settings_sound_label", lang))
        self.btn_test_tg.configure(text=t("settings_test_tg_btn", lang))
        self.btn_save_settings.configure(text=t("settings_save_btn", lang))

        # Guide header
        self.lbl_guide_title.configure(text=t("tab_guide", lang))

        # Dashboard metadata line & state
        self.lbl_metadata.configure(text=self._get_metadata_summary_text())
        self._update_ui_state(is_scanning=self.scanner.is_scanning)

    # =========================================================================
    # GLOBAL HOTKEY MANAGEMENT
    # =========================================================================
    def _register_global_hotkey(self, hotkey_str: str) -> None:
        """Safely binds global toggle hotkey using keyboard library."""
        lang = self.cfg.get("language", "en")
        try:
            import keyboard

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
    def _get_current_monitor_label(self) -> str:
        """Returns clean display name with resolution."""
        idx = self.scanner.display_index
        if 0 <= idx < len(self.monitors):
            return self.monitors[idx]["label"]
        return "Display 1"

    def _get_metadata_summary_text(self) -> str:
        """Constructs clean single-line metadata summary."""
        lang = self.cfg.get("language", "en")
        display_str = self._get_current_monitor_label()
        audio_str = (
            t("audio_enabled", lang)
            if self.cfg.get("sound_enabled", True)
            else t("audio_disabled", lang)
        )
        return t(
            "metadata_summary",
            lang,
            display=display_str,
            hotkey=self._current_hotkey,
            audio=audio_str,
        )

    def log_event(self, message: str) -> None:
        """Appends timestamped message to recent events (retaining last 5)."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self._recent_events.append(entry)
        if len(self._recent_events) > 5:
            self._recent_events = self._recent_events[-5:]

        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("end", "\n".join(self._recent_events) + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear_log(self) -> None:
        """Clears recent activity history."""
        self._recent_events.clear()
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
