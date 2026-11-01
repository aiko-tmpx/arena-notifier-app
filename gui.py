"""Clean, modern Single-Window desktop utility for AikoArenaNotifier.
Features Inter typography, strict grid layout, transparent auto-save,
and high-resolution Windows taskbar/titlebar icon.
"""

from __future__ import annotations

import ctypes
import logging
import os
import sys
import threading
from typing import Dict, List, Optional, Tuple

# Set Windows Application User Model ID for crisp taskbar/titlebar icon grouping
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("aiko.arenanotifier.companion.v1")
except Exception:
    pass

import customtkinter as ctk
from PIL import Image, ImageTk

from config import ConfigManager
from notifier import SoundNotifier, TelegramNotifier, format_queue_pop_message
from scanner import ScreenScanner, get_monitors

logger = logging.getLogger("AikoArenaNotifier.GUI")

# =============================================================================
# COLOR PALETTE CONSTANTS
# =============================================================================
COLOR_BG = "#0F1117"
COLOR_SURFACE_ALT = "#161922"
COLOR_INPUT_BORDER = "#2B3345"
COLOR_INPUT_LOCKED_BG = "#0D0F15"
COLOR_INPUT_LOCKED_BORDER = "#1E2330"
COLOR_INPUT_LOCKED_TEXT = "#64748B"
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


def ensure_and_load_icons() -> None:
    """Ensures UI vector and raster icons (chevron-down, lock, unlock) exist in assets/icons/."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    icons_dir = os.path.join(base_dir, "assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    required_pngs = ["chevron-down.png", "lock.png", "unlock.png"]
    if all(os.path.exists(os.path.join(icons_dir, f)) for f in required_pngs):
        return

    try:
        from PIL import Image, ImageDraw

        # 1. Chevron Down (48x48 supersampled)
        chev_path = os.path.join(icons_dir, "chevron-down.png")
        if not os.path.exists(chev_path):
            scale = 8
            cs = 48 * scale
            unit = cs / 24.0
            stroke = int(2.2 * unit)
            img = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            pts = [(6.5 * unit, 9.5 * unit), (12.0 * unit, 15.0 * unit), (17.5 * unit, 9.5 * unit)]
            draw.line(pts, fill="#94A3B8", width=stroke, joint="round")
            r = stroke / 2.0
            for p in [pts[0], pts[2]]:
                draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill="#94A3B8")
            img.resize((48, 48), Image.Resampling.LANCZOS).save(chev_path)

        # 2. Lock (48x48 supersampled)
        lock_path = os.path.join(icons_dir, "lock.png")
        if not os.path.exists(lock_path):
            scale = 8
            cs = 48 * scale
            unit = cs / 24.0
            stroke = int(2.2 * unit)
            img = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            bx0, by0, bx1, by1 = 3.5 * unit, 11 * unit, 20.5 * unit, 21.5 * unit
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=int(2.5 * unit), outline="#FFFFFF", width=stroke)
            arc_box = [7 * unit, 2.5 * unit, 17 * unit, 12.5 * unit]
            draw.arc(arc_box, start=180, end=0, fill="#FFFFFF", width=stroke)
            draw.line([(7 * unit, 7.5 * unit), (7 * unit, 11.5 * unit)], fill="#FFFFFF", width=stroke)
            draw.line([(17 * unit, 7.5 * unit), (17 * unit, 11.5 * unit)], fill="#FFFFFF", width=stroke)
            draw.ellipse([11 * unit, 15 * unit, 13 * unit, 17 * unit], fill="#FFFFFF")
            img.resize((48, 48), Image.Resampling.LANCZOS).save(lock_path)

        # 3. Unlock (48x48 supersampled)
        unlock_path = os.path.join(icons_dir, "unlock.png")
        if not os.path.exists(unlock_path):
            scale = 8
            cs = 48 * scale
            unit = cs / 24.0
            stroke = int(2.2 * unit)
            img = Image.new("RGBA", (cs, cs), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            bx0, by0, bx1, by1 = 3.5 * unit, 11 * unit, 20.5 * unit, 21.5 * unit
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=int(2.5 * unit), outline="#FFFFFF", width=stroke)
            arc_box = [7 * unit, 2.5 * unit, 17 * unit, 12.5 * unit]
            draw.arc(arc_box, start=180, end=15, fill="#FFFFFF", width=stroke)
            draw.line([(7 * unit, 7.5 * unit), (7 * unit, 11.5 * unit)], fill="#FFFFFF", width=stroke)
            tip_x, tip_y = 16.5 * unit, 6.2 * unit
            r = stroke / 2.0
            draw.ellipse([tip_x - r, tip_y - r, tip_x + r, tip_y + r], fill="#FFFFFF")
            draw.ellipse([11 * unit, 15 * unit, 13 * unit, 17 * unit], fill="#FFFFFF")
            img.resize((48, 48), Image.Resampling.LANCZOS).save(unlock_path)

    except Exception as e:
        logger.debug(f"Failed ensuring icon assets: {e}")


def set_app_icon(window: ctk.CTk, icon_filename: str = "assets/icon.ico") -> None:
    """Sets multi-resolution icon for Windows taskbar and titlebar,
    using direct Win32 WM_SETICON injection to ensure crisp display on high-DPI taskbars.
    """
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, icon_filename)
    png_path = os.path.join(base_dir, "assets", "icon.png")

    # 1. Fallback Tk PhotoImages across multiple sizes
    photos = []
    if os.path.exists(png_path):
        try:
            base_img = Image.open(png_path).convert("RGBA")
            for size in (256, 128, 64, 48, 32, 16):
                photos.append(ImageTk.PhotoImage(base_img.resize((size, size), Image.Resampling.LANCZOS)))
            window.wm_iconphoto(True, *photos)
            window._icon_photos_ref = photos
        except Exception as e:
            logger.debug(f"Failed setting wm_iconphoto: {e}")

    # 2. Tkinter iconbitmap
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception as e:
            logger.debug(f"Failed setting iconbitmap: {e}")

    # 3. Direct Win32 WM_SETICON injection (bypasses Tkinter's 32x32 hard limit)
    if sys.platform == "win32" and os.path.exists(icon_path):
        try:
            window.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id()) or window.winfo_id()
            abs_ico_path = os.path.abspath(icon_path)

            from ctypes import wintypes

            ctypes.windll.user32.LoadImageW.restype = ctypes.c_void_p
            ctypes.windll.user32.LoadImageW.argtypes = [
                wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                ctypes.c_int, ctypes.c_int, wintypes.UINT
            ]
            ctypes.windll.user32.SendMessageW.restype = ctypes.c_void_p
            ctypes.windll.user32.SendMessageW.argtypes = [
                ctypes.c_void_p, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p
            ]

            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            h_big = ctypes.windll.user32.LoadImageW(None, abs_ico_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
            h_small = ctypes.windll.user32.LoadImageW(None, abs_ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)

            if h_big:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_big)
            if h_small:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
        except Exception as e:
            logger.debug(f"Failed setting native Win32 icons: {e}")


class CleanOptionMenu(ctk.CTkOptionMenu):
    """OptionMenu replacing default blurry bitmap arrow with a clean high-resolution chevron,
    cohesive dark-theme button styling, and borderless dark dropdown popup.
    """

    def __init__(self, *args, chevron_image: Optional[ctk.CTkImage] = None, **kwargs):
        self._custom_chevron_image = chevron_image
        self._custom_chevron_photo = None

        # Cohesive dark-theme defaults: subtle dark slate button, no harsh neon purple block
        kwargs.setdefault("fg_color", COLOR_SURFACE_ALT)
        kwargs.setdefault("button_color", "#1F2432")
        kwargs.setdefault("button_hover_color", "#2B3346")
        kwargs.setdefault("dropdown_fg_color", COLOR_SURFACE_ALT)
        kwargs.setdefault("dropdown_hover_color", COLOR_ACCENT)
        kwargs.setdefault("dropdown_text_color", COLOR_TEXT_PRIMARY)

        super().__init__(*args, **kwargs)

        # Eliminate thick Windows 3D/white border on the dropdown menu
        try:
            self._dropdown_menu.configure(borderwidth=0, activeborderwidth=0, relief="flat")
        except Exception:
            pass

    def _draw(self, no_color_updates: bool = False) -> None:
        super()._draw(no_color_updates)
        self._draw_clean_chevron()

    def _draw_clean_chevron(self) -> None:
        self._canvas.delete("dropdown_arrow")
        self._canvas.delete("clean_chevron")

        x = self._apply_widget_scaling(self._current_width - (self._current_height / 2))
        y = self._apply_widget_scaling(self._current_height / 2)

        if self._custom_chevron_image is not None:
            photo = self._custom_chevron_image.create_scaled_photo_image(
                self._get_widget_scaling(),
                self._get_appearance_mode(),
            )
            self._custom_chevron_photo = photo
            self._canvas.create_image(x, y, image=photo, tags="clean_chevron")
        else:
            size = round(4 * self._get_widget_scaling())
            self._canvas.create_line(
                x - size,
                y - round(size * 0.6),
                x,
                y + round(size * 0.6),
                x + size,
                y - round(size * 0.6),
                tags="clean_chevron",
                width=max(1, round(1.8 * self._get_widget_scaling())),
                fill=COLOR_TEXT_MUTED,
                capstyle="round",
                joinstyle="round",
            )


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

        # Debounce timer for auto-save
        self._save_after_id = None

        # Window dimensions: Fixed 540x510 px
        self.title("AikoArenaNotifier")
        self.geometry("540x510")
        self.minsize(540, 510)
        self.maxsize(540, 510)
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Set High-Resolution Windows App Icon
        set_app_icon(self)

        # Ensure and load UI icons
        ensure_and_load_icons()
        self._load_icons()

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

    def _init_typography(self) -> None:
        """Initializes typography scale using Inter."""
        self.font_btn_main = ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        self.font_subtitle = ctk.CTkFont(family=FONT_FAMILY, size=13)
        self.font_form_label = ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")
        self.font_input = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.font_checkbox = ctk.CTkFont(family=FONT_FAMILY, size=13)
        self.font_btn_action = ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")
        self.font_footer = ctk.CTkFont(family=FONT_FAMILY, size=11)

    def _load_icons(self) -> None:
        """Loads high-resolution UI icons for dropdown chevrons and lock toggles."""
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(base_dir, "assets", "icons")

        chev_path = os.path.join(icons_dir, "chevron-down.png")
        if os.path.exists(chev_path):
            chev_img = Image.open(chev_path)
            self.icon_chevron = ctk.CTkImage(light_image=chev_img, dark_image=chev_img, size=(12, 12))
        else:
            self.icon_chevron = None

        lock_path = os.path.join(icons_dir, "lock.png")
        if os.path.exists(lock_path):
            lock_img = Image.open(lock_path)
            self.icon_lock = ctk.CTkImage(light_image=lock_img, dark_image=lock_img, size=(16, 16))
        else:
            self.icon_lock = None

        unlock_path = os.path.join(icons_dir, "unlock.png")
        if os.path.exists(unlock_path):
            unlock_img = Image.open(unlock_path)
            self.icon_unlock = ctk.CTkImage(light_image=unlock_img, dark_image=unlock_img, size=(16, 16))
        else:
            self.icon_unlock = None

    def toggle_token_lock(self) -> None:
        """Toggles read-only lock state for Telegram Bot Token entry."""
        self._token_locked = not self._token_locked
        self._update_token_lock_ui()
        if not self._token_locked:
            self.entry_token.focus()

    def _update_token_lock_ui(self) -> None:
        """Updates visual styling and state for Bot Token input based on lock state."""
        if self._token_locked:
            self.entry_token.configure(
                state="readonly",
                text_color=COLOR_INPUT_LOCKED_TEXT,
                fg_color=COLOR_INPUT_LOCKED_BG,
                border_color=COLOR_INPUT_LOCKED_BORDER,
            )
            self.btn_lock_token.configure(
                image=self.icon_lock,
                fg_color="#1E2433",
                hover_color="#2B3345",
            )
        else:
            self.entry_token.configure(
                state="normal",
                text_color=COLOR_TEXT_PRIMARY,
                fg_color=COLOR_SURFACE_ALT,
                border_color=COLOR_INPUT_BORDER,
            )
            self.btn_lock_token.configure(
                image=self.icon_unlock,
                fg_color="#374151",
                hover_color="#4B5563",
            )

    def toggle_chat_id_lock(self) -> None:
        """Toggles read-only lock state for Telegram Chat ID entry."""
        self._chat_id_locked = not self._chat_id_locked
        self._update_chat_id_lock_ui()
        if not self._chat_id_locked:
            self.entry_chat_id.focus()

    def _update_chat_id_lock_ui(self) -> None:
        """Updates visual styling and state for Chat ID input based on lock state."""
        if self._chat_id_locked:
            self.entry_chat_id.configure(
                state="readonly",
                text_color=COLOR_INPUT_LOCKED_TEXT,
                fg_color=COLOR_INPUT_LOCKED_BG,
                border_color=COLOR_INPUT_LOCKED_BORDER,
            )
            self.btn_lock_chat_id.configure(
                image=self.icon_lock,
                fg_color="#1E2433",
                hover_color="#2B3345",
            )
        else:
            self.entry_chat_id.configure(
                state="normal",
                text_color=COLOR_TEXT_PRIMARY,
                fg_color=COLOR_SURFACE_ALT,
                border_color=COLOR_INPUT_BORDER,
            )
            self.btn_lock_chat_id.configure(
                image=self.icon_unlock,
                fg_color="#374151",
                hover_color="#4B5563",
            )

    def _setup_layout(self) -> None:
        """Constructs compact single-window layout using strictly .grid()."""
        # Root grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main wrapper frame with proper breathing room
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=32, pady=(20, 24))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # ROW 0: Master Action Button
        self.btn_master = ctk.CTkButton(
            self.main_frame,
            text="Start Monitoring",
            font=self.font_btn_main,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            height=54,
            corner_radius=10,
            command=self.on_start_toggle,
        )
        self.btn_master.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        # ROW 1: Status Subtitle
        self.lbl_status = ctk.CTkLabel(
            self.main_frame,
            text="Status: Standing by",
            font=self.font_subtitle,
            text_color=COLOR_TEXT_MUTED,
            anchor="center",
        )
        self.lbl_status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # ROW 2: Separator 1
        sep1 = ctk.CTkFrame(self.main_frame, height=1, fg_color=COLOR_DIVIDER)
        sep1.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # ROW 3: Form - Telegram Bot Token Label
        self.lbl_token = ctk.CTkLabel(
            self.main_frame,
            text="Telegram Bot Token",
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_token.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 2))

        # ROW 4: Form - Telegram Bot Token Container (Entry + Lock Button)
        self.token_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.token_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.token_frame.grid_columnconfigure(0, weight=1)
        self.token_frame.grid_columnconfigure(1, weight=0)

        self.entry_token = ctk.CTkEntry(
            self.token_frame,
            show="*",
            font=self.font_input,
            height=36,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_token.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        if self.cfg.get("telegram_bot_token"):
            self.entry_token.insert(0, self.cfg["telegram_bot_token"])
        self.entry_token.bind("<KeyRelease>", self._on_entry_key_release)
        self.entry_token.bind("<FocusOut>", self._on_entry_focus_out)

        self._token_locked = bool(self.cfg.get("telegram_bot_token"))
        self.btn_lock_token = ctk.CTkButton(
            self.token_frame,
            text="",
            image=self.icon_lock if self._token_locked else self.icon_unlock,
            width=36,
            height=36,
            corner_radius=6,
            fg_color="#1E2433" if self._token_locked else "#374151",
            hover_color="#2B3345" if self._token_locked else "#4B5563",
            command=self.toggle_token_lock,
        )
        self.btn_lock_token.grid(row=0, column=1, sticky="e")
        self._update_token_lock_ui()

        # ROW 5: Form - Telegram Chat ID Label
        self.lbl_chat_id = ctk.CTkLabel(
            self.main_frame,
            text="Telegram Chat ID",
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_chat_id.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 2))

        # ROW 6: Form - Telegram Chat ID Container (Entry + Lock Button)
        self.chat_id_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.chat_id_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.chat_id_frame.grid_columnconfigure(0, weight=1)
        self.chat_id_frame.grid_columnconfigure(1, weight=0)

        self.entry_chat_id = ctk.CTkEntry(
            self.chat_id_frame,
            font=self.font_input,
            height=36,
            corner_radius=8,
            fg_color=COLOR_SURFACE_ALT,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
        )
        self.entry_chat_id.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        if self.cfg.get("telegram_chat_id"):
            self.entry_chat_id.insert(0, str(self.cfg["telegram_chat_id"]))
        self.entry_chat_id.bind("<KeyRelease>", self._on_entry_key_release)
        self.entry_chat_id.bind("<FocusOut>", self._on_entry_focus_out)

        self._chat_id_locked = bool(self.cfg.get("telegram_chat_id"))
        self.btn_lock_chat_id = ctk.CTkButton(
            self.chat_id_frame,
            text="",
            image=self.icon_lock if self._chat_id_locked else self.icon_unlock,
            width=36,
            height=36,
            corner_radius=6,
            fg_color="#1E2433" if self._chat_id_locked else "#374151",
            hover_color="#2B3345" if self._chat_id_locked else "#4B5563",
            command=self.toggle_chat_id_lock,
        )
        self.btn_lock_chat_id.grid(row=0, column=1, sticky="e")
        self._update_chat_id_lock_ui()

        # ROW 7: Form - Target Game Display Label
        self.lbl_display = ctk.CTkLabel(
            self.main_frame,
            text="Target Game Display",
            font=self.font_form_label,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_display.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 2))

        # ROW 8: Form - Target Game Display OptionMenu (with auto-save)
        monitor_labels = [m["label"] for m in self.monitors]
        selected_mon_idx = self.cfg.get("selected_display_index", 0)
        default_mon_label = (
            monitor_labels[selected_mon_idx]
            if 0 <= selected_mon_idx < len(monitor_labels)
            else monitor_labels[0]
        )

        self.opt_display = CleanOptionMenu(
            self.main_frame,
            values=monitor_labels,
            font=self.font_input,
            height=36,
            corner_radius=8,
            chevron_image=self.icon_chevron,
            command=lambda _: self.auto_save(),
        )
        self.opt_display.set(default_mon_label)
        self.opt_display.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # ROW 9: Form - Host Audio Alert Checkbox (with auto-save)
        self.chk_sound = ctk.CTkCheckBox(
            self.main_frame,
            text="Play audio alert on host PC",
            font=self.font_checkbox,
            text_color=COLOR_TEXT_PRIMARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
            command=self.auto_save,
        )
        if self.cfg.get("sound_enabled", True):
            self.chk_sound.select()
        else:
            self.chk_sound.deselect()
        self.chk_sound.grid(row=9, column=0, columnspan=2, sticky="w", pady=(2, 10))

        # ROW 10: Separator 2
        sep2 = ctk.CTkFrame(self.main_frame, height=1, fg_color=COLOR_DIVIDER)
        sep2.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # ROW 11: Action Button: Test Telegram Connection
        self.btn_test = ctk.CTkButton(
            self.main_frame,
            text="Test Telegram Connection",
            font=self.font_btn_action,
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_BTN_HOVER,
            height=42,
            corner_radius=8,
            command=self.on_test_connection,
        )
        self.btn_test.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # ROW 12: Inline Status Feedback
        self.lbl_feedback = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=self.font_footer,
            text_color=COLOR_TEXT_MUTED,
            anchor="center",
        )
        self.lbl_feedback.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 2))

    # =========================================================================
    # TRANSPARENT AUTO-SAVE SYSTEM
    # =========================================================================
    def _on_entry_key_release(self, event=None) -> None:
        """Debounces auto-save on entry key typing."""
        if self._save_after_id:
            try:
                self.after_cancel(self._save_after_id)
            except Exception:
                pass
        self._save_after_id = self.after(400, self.auto_save)

    def _on_entry_focus_out(self, event=None) -> None:
        """Auto-saves immediately on input blur."""
        self.auto_save()

    def auto_save(self) -> None:
        """Saves current state to config.json automatically without user intervention."""
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()
        sound = bool(self.chk_sound.get())

        selected_label = self.opt_display.get()
        selected_idx = 0
        for idx, m in enumerate(self.monitors):
            if m["label"] == selected_label:
                selected_idx = idx
                break

        updated_data = {
            "telegram_bot_token": token,
            "telegram_chat_id": chat_id,
            "selected_display_index": selected_idx,
            "sound_enabled": sound,
            "language": "en",
        }

        self.config_manager.save_config(updated_data)
        self.cfg = self.config_manager.load_config()
        self.scanner.display_index = selected_idx

    # =========================================================================
    # MASTER ACTION CONTROLLER
    # =========================================================================
    def on_start_toggle(self) -> None:
        """Toggles scanner state between IDLE and SCANNING."""
        self.auto_save()
        if self.scanner.is_scanning:
            self.stop_scanning()
        else:
            self.start_scanning()

    def toggle_scanning(self) -> None:
        """Alias to toggle scanning programmatically."""
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
        if is_scanning:
            btn_title = "Monitoring Active..."
            subtitle = "Status: Scanning for queue marker..."
            btn_color = COLOR_SCANNING
            btn_hover = COLOR_SCANNING_HOVER
            sub_color = COLOR_STATUS_ACTIVE
        else:
            btn_title = "Start Monitoring"
            subtitle = "Status: Standing by"
            btn_color = COLOR_ACCENT
            btn_hover = COLOR_ACCENT_HOVER
            sub_color = COLOR_TEXT_MUTED

        self.btn_master.configure(
            text=btn_title,
            fg_color=btn_color,
            hover_color=btn_hover,
        )
        self.lbl_status.configure(
            text=subtitle,
            text_color=sub_color,
        )

    def _on_scanner_tick(self, rgb: Tuple[int, int, int]) -> None:
        """Scanner tick hook."""
        pass

    def _on_scanner_pop(self) -> None:
        """Invoked when pop marker is detected. Marshals to GUI thread."""
        self.after(0, self._handle_queue_pop)

    def _handle_queue_pop(self) -> None:
        """Handles queue pop: auto-stop, audio chime, and Telegram alert."""
        self._update_ui_state(is_scanning=False)

        # 1. Local PC sound alert
        if self.cfg.get("sound_enabled", True):
            self.sound_notifier.play_pop_sound(enabled=True)

        # 2. Telegram push notification
        token = self.cfg.get("telegram_bot_token", "").strip()
        chat_id = self.cfg.get("telegram_chat_id", "").strip()

        if token and chat_id:
            def _send_worker():
                msg = format_queue_pop_message("en")
                ok, err = self.telegram_notifier.send_message(token, chat_id, msg)
                self.after(0, self._on_telegram_result, ok, err)

            threading.Thread(target=_send_worker, daemon=True, name="TgSendThread").start()

    def _on_telegram_result(self, ok: bool, err_msg: str) -> None:
        """Updates feedback label on Telegram send outcome."""
        if ok:
            self.lbl_feedback.configure(
                text="Connection verified!",
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_feedback.configure(
                text=f"Connection failed: {err_msg}",
                text_color=COLOR_DANGER,
            )

    # =========================================================================
    # TEST CONNECTION ACTION
    # =========================================================================
    def on_test_connection(self) -> None:
        """Tests Telegram connection in background thread."""
        self.auto_save()
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token:
            self.lbl_feedback.configure(
                text="Error: Bot Token cannot be empty",
                text_color=COLOR_DANGER,
            )
            return

        if not chat_id:
            self.lbl_feedback.configure(
                text="Error: Chat ID cannot be empty",
                text_color=COLOR_DANGER,
            )
            return

        self.lbl_feedback.configure(
            text="Testing connection...",
            text_color=COLOR_ACCENT,
        )
        self.btn_test.configure(state="disabled")

        def _test_worker():
            ok, msg = self.telegram_notifier.test_connection(token, chat_id, "en")
            self.after(0, self._on_test_finished, ok, msg)

        threading.Thread(target=_test_worker, daemon=True, name="TgTestThread").start()

    def _on_test_finished(self, ok: bool, msg: str) -> None:
        """Handles completion of Telegram connection test."""
        self.btn_test.configure(state="normal")

        if ok:
            self.lbl_feedback.configure(
                text=f"Connection verified! ({msg})",
                text_color=COLOR_STATUS_ACTIVE,
            )
        else:
            self.lbl_feedback.configure(
                text=f"Connection failed: {msg}",
                text_color=COLOR_DANGER,
            )

    def on_closing(self) -> None:
        """Performs clean shutdown on window close with auto-save."""
        logger.info("Application shutting down...")
        self.auto_save()
        self.scanner.stop()
        self.destroy()
