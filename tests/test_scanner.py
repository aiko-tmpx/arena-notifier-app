import pytest
from scanner import is_magenta_pop, get_monitors, calculate_target_coords


def test_is_magenta_pop_true():
    # Exact magenta
    assert is_magenta_pop(255, 0, 255) is True
    # Near magenta within tolerance (R > 230, G < 20, B > 230)
    assert is_magenta_pop(235, 10, 240) is True
    assert is_magenta_pop(250, 19, 250) is True
    assert is_magenta_pop(245, 0, 254) is True


def test_is_magenta_pop_false():
    # White
    assert is_magenta_pop(255, 255, 255) is False
    # Black
    assert is_magenta_pop(0, 0, 0) is False
    # Red only
    assert is_magenta_pop(255, 0, 0) is False
    # Blue only
    assert is_magenta_pop(0, 0, 255) is False
    # Green present
    assert is_magenta_pop(255, 50, 255) is False
    # Dim magenta
    assert is_magenta_pop(200, 0, 200) is False
    # Edge values
    assert is_magenta_pop(230, 10, 255) is False
    assert is_magenta_pop(255, 20, 255) is False
    assert is_magenta_pop(255, 10, 230) is False


def test_calculate_target_coords():
    # Primary monitor at origin (0, 0)
    assert calculate_target_coords(0, 0) == (2, 2)
    # Secondary monitor to the right at (1920, 0)
    assert calculate_target_coords(1920, 0) == (1922, 2)
    # Monitor to the left at (-1920, 0)
    assert calculate_target_coords(-1920, 0) == (-1918, 2)
    # Custom offset
    assert calculate_target_coords(2560, 1440, offset_x=2, offset_y=2) == (2562, 1442)


def test_get_monitors_returns_valid_list():
    monitors = get_monitors()
    assert isinstance(monitors, list)
    assert len(monitors) >= 1
    
    first = monitors[0]
    assert "id" in first
    assert "name" in first
    assert "x" in first
    assert "y" in first
    assert "width" in first
    assert "height" in first
    assert "is_primary" in first
    assert "label" in first
    assert first["width"] > 0
    assert first["height"] > 0
