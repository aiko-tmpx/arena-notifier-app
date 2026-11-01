# AikoArenaNotifier

**AikoArenaNotifier** is a high-performance, modern desktop companion application built with Python and CustomTkinter. It monitors World of Warcraft PvP queue status and delivers instantaneous Telegram push notifications and local audio alerts the millisecond an Arena, Solo Shuffle, or Battleground queue pops.

Designed to work directly alongside the companion World of Warcraft addon **AikoArenaNotifier**.

---

## 🛡️ Zero-Tolerance Anti-Cheat Safety (Hard Guardrails)

The core engineering constraint of this application is **100% complete safety against Blizzard's Warden anti-cheat**.

1. **Zero Game Process Interaction**:
   - **Never** calls `OpenProcess`, `CreateRemoteThread`, `VirtualAllocEx`, `ReadProcessMemory`, or `WriteProcessMemory`.
   - **Never** inspects, hooks, enumerates, or attaches handles or debuggers to `Wow.exe`.
   - **Never** injects DLLs or hooks DirectX/Vulkan/D3D presentation layers.
2. **Zero Synthetic Gameplay Input**:
   - The application is **strictly passive**. It only reads desktop screen pixels and sends network notifications.
   - **Never** generates synthetic keyboard or mouse inputs (`SendInput`, `PostMessage`, mouse clicks to click "Enter Battle").
3. **Passive OS-Level Desktop Capture Only**:
   - Pixel sampling operates strictly at the Windows OS desktop presentation level (`GetDC(NULL)` + `GetPixel` / `mss`).
   - This behavior is completely indistinguishable from standard desktop utilities like OBS Studio, Discord screen sharing, or the Windows Snipping Tool.

---

## ⚡ How It Works

1. **Companion WoW Addon**:
   - Located at: `World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier\`
   - When an Arena, Solo Shuffle, or Battleground queue pop confirmation appears, the addon displays a 5x5 square at the top-left corner of the screen (`UIParent` `(0, 0)`) for 3 seconds.
   - Test command in WoW: `/aan test`.
2. **Desktop Scanner**:
   - Samples pixel `(X: 2, Y: 2)` on the selected game display every ~300ms.
   - Equipped with Windows High-DPI Awareness (Per-Monitor v2) to ensure 1:1 physical pixel sampling across multi-monitor setups.
   - Color detector tolerates monitor HDR and color management variance.
3. **Instant Alert & Auto-Stop**:
   - As soon as the indicator color is confirmed, the scanner **instantly auto-stops** to prevent duplicate alerts and Telegram rate-limiting.
   - Plays a crisp multi-frequency audio chime on the PC speaker (`winsound.Beep`).
   - Dispatches a Markdown-formatted push alert to Telegram via the Bot API.
4. **Re-arming**:
   - When you finish your arena and queue up again, simply press the global hotkey (default **`F9`**) to re-arm the scanner.

---

## 🖥️ UI / UX Design: Single Page Application (SPA)

Built as a sleek, fixed-size Single Page Application window (`780x520`) with a dark theme:

- **Left Navigation Sidebar**:
  - App brand & version badge (`v1.0.0`).
  - Navigation buttons: `[ 📊 Dashboard ]`, `[ ⚙️ Settings ]`, `[ 📖 Guide / Help ]`.
  - Persistent Status Footer:
    - Status indicator dot: `IDLE` (grey/dim) or `SCANNING` (bright emerald green).
    - Active toggle hotkey indicator (`Hotkey: F9`).
- **Right Content Viewport**:
  - **Dashboard**:
    - Hero banner showing active/idle state.
    - Large Action Toggle Button: `START SCANNING (F9)` / `STOP SCANNING (F9)`.
    - Real-time Diagnostics: Target display, sampling point `(2, 2)`, current read RGB, and live dynamic color preview swatch.
    - Scrollable Activity Log with timestamped event tracking and Clear button.
  - **Settings**:
    - Telegram Bot Token input with visibility toggle (👁️ / 🔒).
    - Telegram Chat ID input.
    - Target Game Display dropdown selector (enumerating connected monitors and resolutions).
    - Toggle Hotkey selector (`F8`, `F9`, `F10`, `F11`, `F12`).
    - Sound alert checkbox (enabled by default).
    - `[ Test Telegram Connection ]` and `[ Save Settings ]` action buttons with inline verification feedback.
  - **Guide / Help**:
    - Language switcher: `[ English | Русский ]`.
    - Step-by-step setup cards covering BotFather, UserInfoBot, WoW Addon verification, and anti-cheat explanation.

---

## 🚀 Quick Setup & Installation

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Python 3.10+ (for source installation) or standalone binary

### Running from Source
```powershell
# 1. Clone the repository
git clone https://github.com/aiko-tmpx/arena-notifier-app.git
cd arena-notifier-app

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run the desktop application
python main.py
```

### Running Tests
```powershell
python -m pytest
```

### Building Standalone Executable (.exe)
To compile into a single-file, zero-console Windows `.exe`:
```powershell
.\build_exe.bat
```
The output executable will be generated at `dist\AikoArenaNotifier.exe`.

---

## 📱 Telegram Bot Setup

1. **Create Bot via @BotFather**:
   - Open Telegram and search for `@BotFather`.
   - Send `/newbot`, name your bot (e.g. `MyArenaNotifierBot`).
   - Copy the HTTP API token into the **Settings** tab.
2. **Get Chat ID & Initialize Bot**:
   - **Crucial**: Open your newly created bot in Telegram and click **START** (or send `/start`). Bots cannot initiate a conversation with you until you start it!
   - Search for `@userinfobot` in Telegram and press START.
   - Copy your numeric `Id` (e.g. `123456789`) into the **Chat ID** field in Settings.
   - Click **Test Telegram Connection** in Settings to verify delivery.

---

## 🎮 Companion Addon Verification

The companion addon runs in World of Warcraft:
- Path: `World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier\`
- To test the screen marker at any time in-game:
  ```text
  /aan test
  ```
  This flashes the 5x5 pixel indicator at `(0, 0)` for 3 seconds. The desktop diagnostics swatch will immediately reflect the color change.

---

## ⚖️ License

MIT License. Designed with zero anti-cheat footprint for World of Warcraft competitive PvP players.
