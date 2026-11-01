# AikoArenaNotifier

A modern, production-ready desktop companion application built with Python and CustomTkinter, designed to monitor World of Warcraft arena and Solo Shuffle queues and send instant Telegram push notifications when queues pop.

---

## 🛡️ Zero-Tolerance Anti-Cheat Safety

Safety against Blizzard's Warden anti-cheat is the number one design requirement:
1. **Zero Process Interaction**: The application never touches `Wow.exe` or any game-related process. No `OpenProcess`, no hooks, no memory scanning (`ReadProcessMemory`), and no DLL injection.
2. **Strictly Passive**: No synthetic mouse or keyboard inputs are ever generated or sent into the game.
3. **OS-Level Desktop Sampling Only**: Pixel monitoring operates solely on the Windows OS desktop presentation buffer (`GetDC(NULL)` / `mss`), exactly identical to Discord screen sharing, OBS Studio, or Windows Snipping Tool.

---

## ✨ Features

- **Single Page Application (SPA)**: Sleek, responsive dark-themed UI built with CustomTkinter.
- **Instant Telegram Push Notifications**: High-priority push alerts delivered to your phone with queue details.
- **Local Audio Chime**: Audible multi-frequency chime on the PC speaker when a pop is detected.
- **Multi-Monitor & High-DPI Support**: Accurate pixel sampling across multi-display setups with Windows DPI scaling awareness.
- **Global Toggle Hotkey**: Arm and disarm scanning with a customizable hotkey (default `F9`).
- **Auto-Stop Safety**: Automatically stops scanning upon detection to prevent notification spam.
- **Bilingual Guide**: Built-in interactive setup guide in English and Russian.
- **Companion WoW Addon**: Lightweight, performant Lua addon rendering a 5x5 magenta indicator during queue pops.

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10/11 (64-bit)
- Python 3.10+ (or precompiled binary)

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/aiko-tmpx/arena-notifier-app.git
cd arena-notifier-app

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### 3. WoW Addon Installation
Copy the `addon/AikoArenaNotifier` folder into your World of Warcraft directory:
`World of Warcraft\_retail_\Interface\AddOns\`
