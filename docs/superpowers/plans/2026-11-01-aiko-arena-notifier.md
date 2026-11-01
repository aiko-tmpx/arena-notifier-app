# AikoArenaNotifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready, clean, modern desktop companion application called "AikoArenaNotifier" using Python and CustomTkinter, designed to work alongside a companion World of Warcraft addon with zero anti-cheat risk.

**Architecture:** A Single Page Application (SPA) architecture in Python CustomTkinter (Dark theme) with a modular backend: a thread-safe desktop-level screen scanner capturing pixel (2,2) on a selected monitor, a Telegram Bot API notification dispatcher with local sound alert, a persistent JSON configuration manager, multi-language localization (EN/RU), and support for the companion WoW Lua addon.

**Tech Stack:** Python 3.14+, `customtkinter`, `keyboard`, `mss`, `requests`, `screeninfo`, `pytest`, Win32 GDI / Windows API (`ctypes`, `winsound`), WoW Lua API 11.0+.

**Spec:** User specification for AikoArenaNotifier (Desktop SPA, Zero-Tolerance Anti-Cheat Safety, Telegram Bot push notification, CustomTkinter dark theme, global hotkey, companion WoW addon).

## Global Constraints

- ZERO-TOLERANCE ANTI-CHEAT SAFETY: Never touch WoW process, never hook or read memory, never inject synthetic input back to the game. Only passive OS-level desktop display buffer pixel capture.
- UI must remain 100% fluid: all network calls and screen captures must run in background daemon threads.
- Thread-safe UI updates via `root.after()`.
- Windows High-DPI Awareness enabled to ensure 1:1 physical pixel accuracy across displays.
- Detection tolerance: Target color condition supports both companion addon purple (`#A330C9`, RGB 163, 48, 201) and pure magenta (`#FF00FF`).
- Single Page Application (SPA) fixed window layout (780x520) with left navigation sidebar and 3 viewports: Dashboard, Settings, Guide.

## Review Focus

1. Monitor coordinates & DPI scaling: Target pixel (2,2) must correctly map to physical pixels with monitor offset `(x + 2, y + 2)` under multi-monitor and High-DPI configurations.
2. Network resilience: Telegram notifications must have explicit timeouts and catch network/SSL/token errors without crashing or freezing the UI.
3. Auto-stop guarantee: Scanner must instantly set its scanning state to `False` before firing notifications to avoid duplicate triggers and rate limit hits.
4. Hotkey safety: Global hotkey unhooks cleanly on shutdown and re-registers cleanly when changed in settings without ghost triggers.
5. Addon companion compatibility: Compatible with companion WoW addon at `f:\Games\World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier\` (`/aan test`).

---

### Task 1: Project Scaffolding & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`

- [x] **Step 1: Create `requirements.txt`**
- [x] **Step 2: Create `.gitignore`**
- [x] **Step 3: Create initial `README.md`**
- [x] **Step 4: Commit scaffolding**

---

### Task 2: Configuration Manager (`config.py`)

**Files:**
- Create: `config.py`
- Test: `tests/test_config.py`

- [x] **Step 1: Write test for configuration manager**
- [x] **Step 2: Run test to verify failure**
- [x] **Step 3: Implement `config.py`**
- [x] **Step 4: Run test to verify passing**
- [x] **Step 5: Commit config module**

---

### Task 3: Localization System (`localization.py`)

**Files:**
- Create: `localization.py`
- Test: `tests/test_localization.py`

- [x] **Step 1: Write test for localization dictionary completeness**
- [x] **Step 2: Run test to verify failure**
- [x] **Step 3: Implement `localization.py`**
- [x] **Step 4: Run test to verify passing**
- [x] **Step 5: Commit localization module**

---

### Task 4: Passive Screen Scanner & Anti-Cheat Safe Monitor Capture (`scanner.py`)

**Files:**
- Create: `scanner.py`
- Test: `tests/test_scanner.py`

- [x] **Step 1: Write unit tests for color detection and monitor coordinate calculations**
- [x] **Step 2: Run test to verify failure**
- [x] **Step 3: Implement `scanner.py`**
- [x] **Step 4: Run test to verify passing**
- [x] **Step 5: Commit scanner module**

---

### Task 5: Push Notifications & Audio Alert (`notifier.py`)

**Files:**
- Create: `notifier.py`
- Test: `tests/test_notifier.py`

- [x] **Step 1: Write unit tests for Telegram message formatting and mock API calls**
- [x] **Step 2: Run test to verify failure**
- [x] **Step 3: Implement `notifier.py`**
- [x] **Step 4: Run test to verify passing**
- [x] **Step 5: Commit notifier module**

---

### Task 6: Companion World of Warcraft Addon Alignment

- [x] **Step 1: Remove duplicate addon folder from desktop app repo per user request**
- [x] **Step 2: Inspect existing addon at `f:\Games\World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier\`**
- [x] **Step 3: Align desktop color detection and slash command documentation with addon (`#A330C9` / `/aan test`)**

---

### Task 7: Single Page Application GUI (`gui.py`) & App Entry Point (`main.py`)

**Files:**
- Create: `gui.py`
- Create: `main.py`
- Test: `tests/test_gui.py`

- [x] **Step 1: Implement `gui.py`**
- [x] **Step 2: Implement `main.py`**
- [x] **Step 3: Smoke test application startup and shutdown in virtual environment**
- [x] **Step 4: Commit GUI and main entry point**

---

### Task 8: Verification, Packaging Script & Documentation

**Files:**
- Create: `build_exe.bat`
- Modify: `README.md`

- [x] **Step 1: Create `build_exe.bat`**
- [x] **Step 2: Update `README.md`**
- [x] **Step 3: Run full test suite**
- [x] **Step 4: Commit final deliverables**
