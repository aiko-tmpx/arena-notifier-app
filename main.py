"""AikoArenaNotifier - Desktop Companion Application
Main entry point and lifecycle manager.
"""

from __future__ import annotations

import argparse
import ctypes
import logging
import os
import sys
import urllib.request

# 1. Enable Windows DPI Awareness and set AppUserModelID for crisp taskbar/titlebar icon
try:
    myappid = "aiko.arenanotifier.companion.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Configure clean logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AikoArenaNotifier.Main")


def ensure_and_load_fonts() -> None:
    """Ensures Inter TTF fonts are available locally and registered into Win32 GDI."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    fonts = {
        "Inter-Regular.ttf": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.ttf",
        "Inter-Bold.ttf": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Bold.ttf",
    }

    for font_name, url in fonts.items():
        dest_path = os.path.join(assets_dir, font_name)
        if not os.path.exists(dest_path):
            try:
                urllib.request.urlretrieve(url, dest_path)
            except Exception:
                continue

        if os.name == "nt" and os.path.exists(dest_path):
            try:
                # FR_PRIVATE (0x10) | FR_NOT_ENUM (0x20)
                ctypes.windll.gdi32.AddFontResourceExW(dest_path, 0x10 | 0x20, 0)
            except Exception as e:
                logger.debug(f"Failed to register font {font_name}: {e}")


# Pre-load Inter font into GDI
ensure_and_load_fonts()

import customtkinter as ctk

from config import ConfigManager
from gui import MainWindow
from notifier import SoundNotifier, TelegramNotifier


def main() -> int:
    """Initializes and runs AikoArenaNotifier."""
    parser = argparse.ArgumentParser(description="AikoArenaNotifier Desktop Application")
    parser.add_argument(
        "--test-run",
        action="store_true",
        help="Initializes UI and exits immediately (used for automated smoke testing)",
    )
    args = parser.parse_args()

    # Configure CustomTkinter Appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Instantiate Backend Subsystems
    config_manager = ConfigManager()
    telegram_notifier = TelegramNotifier()
    sound_notifier = SoundNotifier()

    # Create and Launch Main Single-Window Compact Utility
    app = MainWindow(
        config_manager=config_manager,
        telegram_notifier=telegram_notifier,
        sound_notifier=sound_notifier,
    )
    app.protocol("WM_DELETE_WINDOW", app.on_closing)

    if args.test_run:
        logger.info("Executing automated smoke test run...")
        app.update()
        app.on_closing()
        logger.info("Smoke test passed successfully!")
        return 0

    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Quitting...")
        app.on_closing()

    return 0


if __name__ == "__main__":
    sys.exit(main())
