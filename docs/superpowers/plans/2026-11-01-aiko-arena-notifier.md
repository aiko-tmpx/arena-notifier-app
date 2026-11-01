# AikoArenaNotifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready, clean, modern desktop companion application called "AikoArenaNotifier" using Python and CustomTkinter, designed to work alongside a companion World of Warcraft addon with zero anti-cheat risk.

**Architecture:** A Single Page Application (SPA) architecture in Python CustomTkinter (Dark theme) with a modular backend: a thread-safe desktop-level screen scanner capturing pixel (2,2) on a selected monitor, a Telegram Bot API notification dispatcher with local sound alert, a persistent JSON configuration manager, multi-language localization (EN/RU), and a companion WoW Lua addon.

**Tech Stack:** Python 3.14+, `customtkinter`, `keyboard`, `mss`, `requests`, `screeninfo`, `pytest`, Win32 GDI / Windows API (`ctypes`, `winsound`), WoW Lua API 11.0+.

**Spec:** User specification for AikoArenaNotifier (Desktop SPA, Zero-Tolerance Anti-Cheat Safety, Telegram Bot push notification, CustomTkinter dark theme, global hotkey, companion WoW addon).

## Global Constraints

- ZERO-TOLERANCE ANTI-CHEAT SAFETY: Never touch WoW process, never hook or read memory, never inject synthetic input back to the game. Only passive OS-level desktop display buffer pixel capture.
- UI must remain 100% fluid: all network calls and screen captures must run in background daemon threads.
- Thread-safe UI updates via `root.after()`.
- Windows High-DPI Awareness enabled to ensure 1:1 physical pixel accuracy across displays.
- Detection tolerance: Target color condition is RGB check ($R > 230$, $G < 20$, $B > 230$).
- Single Page Application (SPA) fixed window layout (780x520) with left navigation sidebar and 3 viewports: Dashboard, Settings, Guide.

## Review Focus

1. Monitor coordinates & DPI scaling: Target pixel (2,2) must correctly map to physical pixels with monitor offset `(x + 2, y + 2)` under multi-monitor and High-DPI configurations.
2. Network resilience: Telegram notifications must have explicit timeouts and catch network/SSL/token errors without crashing or freezing the UI.
3. Auto-stop guarantee: Scanner must instantly set its scanning state to `False` before firing notifications to avoid duplicate triggers and rate limit hits.
4. Hotkey safety: Global hotkey unhooks cleanly on shutdown and re-registers cleanly when changed in settings without ghost triggers.
5. Addon companion compatibility: Companion WoW addon must properly trigger on `UPDATE_BATTLEFIELD_STATUS` and provide `/aiko test` for manual verification.

---

### Task 1: Project Scaffolding & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Create `requirements.txt`**
  Specify `customtkinter`, `keyboard`, `mss`, `requests`, `screeninfo`, `pytest`.

- [ ] **Step 2: Create `.gitignore`**
  Ignore Python cache (`__pycache__`, `.pytest_cache`), virtual environment (`.venv`), local config (`config.json`), build artifacts (`dist`, `build`, `*.spec`).

- [ ] **Step 3: Create initial `README.md`**
  Document project overview, zero-tolerance anti-cheat safety principles, architecture, prerequisites, and setup instructions.

- [ ] **Step 4: Commit scaffolding**
  `git add requirements.txt .gitignore README.md && git commit -m "chore: project scaffolding and requirements"`

---

### Task 2: Configuration Manager (`config.py`)

**Files:**
- Create: `config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write test for configuration manager**
  Test default values, loading non-existent file returns defaults, saving updates, sanitization, and fallback to APPDATA.

- [ ] **Step 2: Run test to verify failure**
  Run `pytest tests/test_config.py` to ensure it fails before implementation.

- [ ] **Step 3: Implement `config.py`**
  Implement `ConfigManager` with `DEFAULT_CONFIG`, `load_config()`, `save_config()`, path resolution (`config.json` in local working directory or `%APPDATA%/AikoArenaNotifier/config.json`).

- [ ] **Step 4: Run test to verify passing**
  Run `pytest tests/test_config.py` and ensure 100% pass.

- [ ] **Step 5: Commit config module**
  `git add config.py tests/test_config.py && git commit -m "feat: configuration manager with persistent JSON storage"`

---

### Task 3: Localization System (`localization.py`)

**Files:**
- Create: `localization.py`
- Test: `tests/test_localization.py`

- [ ] **Step 1: Write test for localization dictionary completeness**
  Test that both `'en'` and `'ru'` dictionaries contain identical keys, test key retrieval helper `t(key, lang)`.

- [ ] **Step 2: Run test to verify failure**
  Run `pytest tests/test_localization.py`.

- [ ] **Step 3: Implement `localization.py`**
  Implement English and Russian strings covering all UI views:
  - App title, tabs (Dashboard, Settings, Guide)
  - Hero statuses, button labels, diagnostics descriptions
  - Settings fields, placeholders, tooltips, feedback messages
  - Detailed 4-step setup guide with full explanations for BotFather, UserInfoBot, WoW Addon, and Hotkeys.

- [ ] **Step 4: Run test to verify passing**
  Run `pytest tests/test_localization.py`.

- [ ] **Step 5: Commit localization module**
  `git add localization.py tests/test_localization.py && git commit -m "feat: complete en/ru localization for UI and setup guide"`

---

### Task 4: Passive Screen Scanner & Anti-Cheat Safe Monitor Capture (`scanner.py`)

**Files:**
- Create: `scanner.py`
- Test: `tests/test_scanner.py`

- [ ] **Step 1: Write unit tests for color detection and monitor coordinate calculations**
  Test `is_magenta_pop(r, g, b)` logic for true magenta `(255, 0, 255)`, near-magenta `(240, 10, 245)`, non-magenta `(255, 255, 255)`, `(0, 0, 0)`, `(200, 50, 200)`. Test monitor coordinate offset calculation.

- [ ] **Step 2: Run test to verify failure**
  Run `pytest tests/test_scanner.py`.

- [ ] **Step 3: Implement `scanner.py`**
  - Implement DPI awareness initialization via Win32 `SetProcessDpiAwareness`.
  - Implement `get_monitors()` using `mss` and `screeninfo` fallback, returning list of monitor dicts `{id, name, x, y, width, height, is_primary}`.
  - Implement passive desktop capture using GDI `GetDC(0)` + `GetPixel` with fallback to `mss` grab of 1x1 rect around `(x+2, y+2)`.
  - Implement `ScreenScanner` daemon thread with thread-safe start/stop, tick callback `on_tick(rgb)`, pop callback `on_pop()`, and automatic state reset to IDLE on detection.

- [ ] **Step 4: Run test to verify passing**
  Run `pytest tests/test_scanner.py`.

- [ ] **Step 5: Commit scanner module**
  `git add scanner.py tests/test_scanner.py && git commit -m "feat: passive desktop pixel scanner with DPI awareness and zero anti-cheat footprint"`

---

### Task 5: Push Notifications & Audio Alert (`notifier.py`)

**Files:**
- Create: `notifier.py`
- Test: `tests/test_notifier.py`

- [ ] **Step 1: Write unit tests for Telegram message formatting and mock API calls**
  Test payload construction, error message parsing for invalid tokens (HTTP 401), invalid chat IDs (HTTP 400), connection failures, and test sound fallback.

- [ ] **Step 2: Run test to verify failure**
  Run `pytest tests/test_notifier.py`.

- [ ] **Step 3: Implement `notifier.py`**
  - Implement `TelegramNotifier`:
    - `send_message(token, chat_id, text) -> tuple[bool, str]`
    - `test_connection(token, chat_id) -> tuple[bool, str]`
    - Markdown-formatted queue pop notification with timestamp and reminder to accept queue.
  - Implement `SoundNotifier`:
    - `play_pop_sound(enabled=True)`: crisp high-priority audio chime using Windows `winsound.Beep` sequence (e.g. 1000Hz, 1500Hz, 2000Hz) in a non-blocking background thread.
    - `play_test_sound()`.

- [ ] **Step 4: Run test to verify passing**
  Run `pytest tests/test_notifier.py`.

- [ ] **Step 5: Commit notifier module**
  `git add notifier.py tests/test_notifier.py && git commit -m "feat: telegram push notifier with markdown formatting and host audio alerts"`

---

### Task 6: Companion World of Warcraft Addon (`addon/AikoArenaNotifier`)

**Files:**
- Create: `addon/AikoArenaNotifier/AikoArenaNotifier.toc`
- Create: `addon/AikoArenaNotifier/AikoArenaNotifier.lua`

- [ ] **Step 1: Implement `AikoArenaNotifier.toc`**
  Provide metadata compatible with modern WoW (Interface: 110007 / 110005, Title, Notes, Author, Version).

- [ ] **Step 2: Implement `AikoArenaNotifier.lua`**
  - Create 5x5 pixel frame clamped to TOPLEFT (0,0) with solid `#FF00FF` texture.
  - Register events: `UPDATE_BATTLEFIELD_STATUS`, `PVP_BATTLEGROUND_CONFIRM_ENTRY`, `PLAYER_ENTERING_WORLD`.
  - Scan battlefield statuses 1 to `GetMaxBattlefieldID()`: if status is `"confirm"`, show indicator; otherwise hide.
  - Add slash command `/aiko test` (toggles marker for 5 seconds to test desktop app detection) and `/aiko status`.

- [ ] **Step 3: Verify Lua syntax and commit**
  `git add addon/ && git commit -m "feat: companion World of Warcraft addon with 5x5 magenta queue pop marker"`

---

### Task 7: Single Page Application GUI (`gui.py`) & App Entry Point (`main.py`)

**Files:**
- Create: `gui.py`
- Create: `main.py`

- [ ] **Step 1: Implement `gui.py`**
  - Build CustomTkinter SPA window (780x520) with Dark theme and sleek palette.
  - Left Sidebar: Logo, version badge, navigation buttons with active states, persistent Status Dot + Label (IDLE / SCANNING), Hotkey indicator.
  - View Switcher: Single content frame dynamically swapping Dashboard, Settings, and Guide views with `.grid()` / `.grid_forget()`.
  - Dashboard View: Status hero banner, big action toggle button, diagnostics panel (Monitor, Target Pixel (2,2), Live RGB readout and dynamic color swatch), scrollable activity log with timestamped entries and clear button.
  - Settings View: Masked bot token entry with visibility toggle 👁️, Chat ID entry, Monitor dropdown selector, Hotkey dropdown selector (`F8`–`F12`), Sound alert checkbox, [Test Connection] & [Save Settings] buttons with inline status feedback.
  - Guide View: Language switcher segmented button `[ English | Русский ]`, formatted step-by-step setup cards with code blocks and copyable addon instructions.
  - Global Hotkey Manager: Thread-safe hotkey toggle with dynamic re-registration.

- [ ] **Step 2: Implement `main.py`**
  - DPI awareness initialization.
  - Clean lifecycle management: handle window close event, unhook keyboard hooks, stop scanner thread, save state.
  - Graceful exception logging.

- [ ] **Step 3: Smoke test application startup and shutdown in virtual environment**
  Verify non-interactive test mode / GUI instantiation works without error.

- [ ] **Step 4: Commit GUI and main entry point**
  `git add gui.py main.py && git commit -m "feat: customtkinter single page application with dashboard, settings, and guide views"`

---

### Task 8: Verification, Packaging Script & Documentation

**Files:**
- Create: `build_exe.bat`
- Modify: `README.md`

- [ ] **Step 1: Create `build_exe.bat`**
  Provide one-click PyInstaller script for building a standalone Windows executable.

- [ ] **Step 2: Update `README.md`**
  Include full setup guide, screenshots/diagrams, anti-cheat safety explanation, addon installation guide, troubleshooting, and hotkey instructions.

- [ ] **Step 3: Run full test suite**
  Execute `pytest` across all test files and confirm all pass.

- [ ] **Step 4: Commit final deliverables**
  `git add . && git commit -m "docs: complete user guide, packaging scripts, and project documentation"`
