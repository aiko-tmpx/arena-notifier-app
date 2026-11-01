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


# Pre-load Inter font into GDI and ensure UI icons
ensure_and_load_fonts()
ensure_and_load_icons()

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
