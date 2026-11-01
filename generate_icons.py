"""Generates multi-resolution Windows icon assets (.ico and .png) using Pillow with Lanczos downsampling.
"""

from __future__ import annotations

import os
import sys
from PIL import Image

DEFAULT_SOURCE = r"E:\Images\Pictures\DH Min.png"
SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]


def generate_icon_assets(source_path: str = DEFAULT_SOURCE, output_dir: str = "assets") -> bool:
    """Converts source image into multi-resolution icon.ico and high-res icon.png."""
    os.makedirs(output_dir, exist_ok=True)
    ico_path = os.path.join(output_dir, "icon.ico")
    png_path = os.path.join(output_dir, "icon.png")

    if not os.path.exists(source_path):
        return False

    try:
        img = Image.open(source_path).convert("RGBA")
        img.save(ico_path, format="ICO", sizes=SIZES)
        img.resize((256, 256), Image.Resampling.LANCZOS).save(png_path, format="PNG")
        return True
    except Exception as e:
        print(f"Failed generating icon assets from {source_path}: {e}")
        return False


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE
    out = sys.argv[2] if len(sys.argv) > 2 else "assets"
    success = generate_icon_assets(src, out)
    if success:
        print(f"Icon assets successfully generated from: {src}")
    else:
        print(f"Icon generation skipped or failed for: {src}")
