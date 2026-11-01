"""AikoArenaNotifier - Desktop Companion Application
Main entry point and lifecycle manager.
"""

from __future__ import annotations

import argparse
import logging
import sys

import customtkinter as ctk

from config import ConfigManager
from gui import MainWindow
from notifier import SoundNotifier, TelegramNotifier
from scanner import enable_dpi_awareness

# Configure clean logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AikoArenaNotifier.Main")


def main() -> int:
    """Initializes and runs AikoArenaNotifier."""
    parser = argparse.ArgumentParser(description="AikoArenaNotifier Desktop Application")
    parser.add_argument(
        "--test-run",
        action="store_true",
        help="Initializes UI and exits immediately (used for automated smoke testing)",
    )
    args = parser.parse_args()

    # 1. Enable Windows High-DPI Awareness for 1:1 physical pixel sampling
    dpi_ok = enable_dpi_awareness()
    logger.info(f"Windows High-DPI Awareness initialized: {dpi_ok}")

    # 2. Configure CustomTkinter Appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # 3. Instantiate Backend Subsystems
    config_manager = ConfigManager()
    telegram_notifier = TelegramNotifier()
    sound_notifier = SoundNotifier()

    # 4. Create and Launch Main Single Page Application Window
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
