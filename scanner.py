"""Passive desktop screen scanner for AikoArenaNotifier.

================================================================================
CRITICAL REQUIREMENT #1: ZERO-TOLERANCE ANTI-CHEAT SAFETY (HARD GUARDRAILS)
================================================================================
1. ABSOLUTELY NO INTERACTION WITH THE WOW PROCESS:
   - NEVER call OpenProcess, CreateRemoteThread, VirtualAllocEx, or Read/WriteProcessMemory.
   - NEVER inspect, hook, enumerate, or attach debuggers/handles to Wow.exe.
   - NEVER inject DLLs or hook DirectX/Vulkan/D3D presentation layers.
2. NO SYNTHETIC GAMEPLAY INPUT:
   - STRICTLY PASSIVE. Only reads screen pixels and dispatches external network alerts.
   - NEVER send keyboard/mouse inputs back into the game client.
3. PASSIVE OS-LEVEL DESKTOP CAPTURE ONLY:
   - Pixel sampling operates entirely at the OS desktop level using standard Windows
     GDI GetDC(NULL) + GetPixel or mss display buffer reading.
================================================================================
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple

import mss

logger = logging.getLogger("AikoArenaNotifier.Scanner")


def _get_mss_instance():
    """Returns mss instance supporting both MSS() and legacy mss()."""
    cls = getattr(mss, "MSS", mss.mss)
    return cls()
    """Configures Per-Monitor DPI awareness on Windows for 1:1 pixel accuracy."""
    try:
        # Shcore.dll SetProcessDpiAwareness(2) -> PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return True
    except (AttributeError, OSError):
        try:
            # User32.dll fallback SetProcessDPIAware()
            ctypes.windll.user32.SetProcessDPIAware()
            return True
        except (AttributeError, OSError):
            return False


def enable_dpi_awareness() -> bool:
    """Configures Per-Monitor DPI awareness on Windows for 1:1 pixel accuracy."""
    try:
        # Shcore.dll SetProcessDpiAwareness(2) -> PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return True
    except (AttributeError, OSError):
        try:
            # User32.dll fallback SetProcessDPIAware()
            ctypes.windll.user32.SetProcessDPIAware()
            return True
        except (AttributeError, OSError):
            return False


def is_magenta_pop(r: int, g: int, b: int) -> bool:
    """Checks whether the sampled RGB matches the WoW companion addon's magenta square.
    
    Target is #FF00FF (255, 0, 255). We use an asymmetric threshold check:
    R > 230, G < 20, B > 230 to tolerate slight color profile / HDR differences.
    """
    return r > 230 and g < 20 and b > 230


def calculate_target_coords(
    monitor_x: int, monitor_y: int, offset_x: int = 2, offset_y: int = 2
) -> Tuple[int, int]:
    """Calculates absolute desktop coordinate for pixel (2, 2) inside the 5x5 marker."""
    return monitor_x + offset_x, monitor_y + offset_y


def get_monitors() -> List[Dict]:
    """Enumerates all active desktop displays with coordinate offsets and resolution."""
    monitors: List[Dict] = []
    
    try:
        with _get_mss_instance() as sct:
            # sct.monitors[0] is the virtual "all in one" bounding box monitor.
            # Individual monitors start from index 1.
            individual = sct.monitors[1:]
            if not individual:
                individual = sct.monitors[:1]

            for idx, m in enumerate(individual):
                is_primary = (m["left"] == 0 and m["top"] == 0)
                name = f"Display {idx + 1}"
                resolution = f"{m['width']}x{m['height']}"
                tag = " [Primary]" if is_primary else ""
                label = f"{name} ({resolution}){tag}"
                
                monitors.append({
                    "id": idx,
                    "name": name,
                    "x": m["left"],
                    "y": m["top"],
                    "width": m["width"],
                    "height": m["height"],
                    "is_primary": is_primary,
                    "label": label,
                })
    except Exception as e:
        logger.warning(f"Failed to enumerate monitors via mss: {e}")
        # Fallback single display
        monitors.append({
            "id": 0,
            "name": "Display 1",
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "is_primary": True,
            "label": "Display 1 (1920x1080) [Primary]",
        })

    return monitors


def read_pixel_gdi(x: int, y: int) -> Optional[Tuple[int, int, int]]:
    """Captures RGB of a desktop pixel using Windows GDI GetDC(0) + GetPixel."""
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        
        hdc = user32.GetDC(0)
        if not hdc:
            return None
            
        color = gdi32.GetPixel(hdc, x, y)
        user32.ReleaseDC(0, hdc)
        
        if color == 0xFFFFFFFF or color == -1:
            # CLR_INVALID
            return None

        # GDI COLORREF is 0x00BBGGRR
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        return r, g, b
    except Exception as e:
        logger.debug(f"GDI GetPixel failed: {e}")
        return None


def read_pixel_mss(x: int, y: int) -> Optional[Tuple[int, int, int]]:
    """Captures RGB of a desktop pixel using mss display buffer capture."""
    try:
        with _get_mss_instance() as sct:
            rect = {"left": x, "top": y, "width": 1, "height": 1}
            img = sct.grab(rect)
            # img.pixel(0, 0) returns (R, G, B)
            return img.pixel(0, 0)
    except Exception as e:
        logger.debug(f"mss pixel grab failed: {e}")
        return None


def read_desktop_pixel(x: int, y: int) -> Tuple[int, int, int]:
    """Reads desktop pixel at (x, y) with GDI primary and mss fallback."""
    pixel = read_pixel_gdi(x, y)
    if pixel is not None:
        return pixel

    pixel = read_pixel_mss(x, y)
    if pixel is not None:
        return pixel

    return 0, 0, 0


class ScreenScanner:
    """Thread-safe background screen scanner monitoring target display pixel."""

    def __init__(
        self,
        display_index: int = 0,
        interval_ms: int = 300,
        on_tick: Optional[Callable[[Tuple[int, int, int]], None]] = None,
        on_pop: Optional[Callable[[], None]] = None,
    ) -> None:
        self.display_index = display_index
        self.interval_ms = interval_ms
        self.on_tick = on_tick
        self.on_pop = on_pop

        self._is_scanning = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    @property
    def is_scanning(self) -> bool:
        with self._lock:
            return self._is_scanning

    def get_target_coordinates(self) -> Tuple[int, int]:
        """Resolves target coordinate (X:2, Y:2) on selected display."""
        monitors = get_monitors()
        if 0 <= self.display_index < len(monitors):
            mon = monitors[self.display_index]
        else:
            mon = monitors[0] if monitors else {"x": 0, "y": 0}

        return calculate_target_coords(mon.get("x", 0), mon.get("y", 0))

    def sample_current_pixel(self) -> Tuple[int, int, int]:
        """Performs a single immediate sample of the target pixel."""
        x, y = self.get_target_coordinates()
        return read_desktop_pixel(x, y)

    def start(self) -> bool:
        """Starts scanning in a daemon background thread."""
        with self._lock:
            if self._is_scanning:
                return False
            self._is_scanning = True

        self._thread = threading.Thread(target=self._scan_loop, daemon=True, name="ScannerThread")
        self._thread.start()
        return True

    def stop(self) -> None:
        """Stops the scanning loop gracefully."""
        with self._lock:
            self._is_scanning = False

    def _scan_loop(self) -> None:
        """Continuous background scan loop."""
        logger.info(f"ScreenScanner started on display index {self.display_index}")

        while True:
            with self._lock:
                if not self._is_scanning:
                    break

            try:
                x, y = self.get_target_coordinates()
                r, g, b = read_desktop_pixel(x, y)

                # Report live pixel to UI diagnostics
                if self.on_tick:
                    self.on_tick((r, g, b))

                # Check pop condition
                if is_magenta_pop(r, g, b):
                    logger.info(f"Arena queue pop detected! RGB: ({r}, {g}, {b})")
                    # AUTO-STOP: instantly set is_scanning = False before notifying
                    with self._lock:
                        self._is_scanning = False

                    if self.on_pop:
                        self.on_pop()
                    break

            except Exception as e:
                logger.error(f"Error during scan loop tick: {e}", exc_info=True)

            sleep_time = max(0.05, self.interval_ms / 1000.0)
            time.sleep(sleep_time)

        logger.info("ScreenScanner loop terminated.")
