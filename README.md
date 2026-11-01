# AikoArenaNotifier

[ English ](#english) | [ Русский ](#русский)

---

<a name="english"></a>
## English

### What is this?
A lightweight Windows desktop companion for World of Warcraft (Retail) that sends a Telegram push notification when your Arena or Solo Shuffle queue pops.

It passively reads an on-screen pixel rendered by the companion addon via the Windows desktop buffer (`GetDC(0)`). It does not hook into `Wow.exe`, does not read game memory, and does not simulate inputs.

### Quick Start
1. **Download**: Grab `AikoArenaNotifier.exe` from [Latest Releases](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest).
2. **Addon**: Install the companion addon via [CurseForge](https://www.curseforge.com/wow/addons/aiko-arena-notifier) or [GitHub](https://github.com/aiko-tmpx/arena-notifier-addon) (or drop it into `Interface/AddOns/`). Run `/aan test` in-game to verify the marker.
3. **Launch**: Run `AikoArenaNotifier.exe`. Select your game display and click **Start Monitoring**.

### Telegram Setup (BYOB)
1. Get a **Bot Token**: message [@BotFather](https://t.me/BotFather) (`/newbot`).
2. Get your **Chat ID**: message [@userinfobot](https://t.me/userinfobot) (press Start).
3. **IMPORTANT**: Open your newly created bot in Telegram and press **START** (or send `/start`). Telegram blocks bots from messaging users until the chat is initiated by the user.
4. Paste the Token and Chat ID into the app, click **Test Telegram Connection**, and click **Start Monitoring** when you queue up.

### Anti-Cheat Safety
| Check | Typical Bots / Cheats | AikoArenaNotifier | Status |
| :--- | :--- | :--- | :--- |
| **Process Inspection** | `OpenProcess`, inspects handles, tracks `Wow.exe` PID | None. The app does not know or care if WoW is running. | ✅ Safe |
| **Game Memory** | `ReadProcessMemory` / `WriteProcessMemory` | Zero memory reads. Never inspects RAM. | ✅ Safe |
| **Code Injection** | Hooks DirectX (`Present`/`EndScene`), injects DLLs | None. Standard Python process. | ✅ Safe |
| **Input Emulation** | `SendInput`, `mouse_event` (auto-accept) | None. Purely passive; you accept manually. | ✅ Safe |
| **Pixel Capture** | Proprietary graphics driver hooks | Standard Win32 GDI `GetDC(0)` (same as OBS/Discord). | ✅ Safe |
| **In-Game Addon** | Protected lua exploits | Standard Blizzard UI events (`UPDATE_BATTLEFIELD_STATUS`). | ✅ Safe |

---

<a name="русский"></a>
## Русский

### Что это?
Компактная утилита под Windows для World of Warcraft (Retail), которая отправляет уведомление в Telegram при появлении очереди на Арену или Solo Shuffle.

Работает через пассивное чтение системного пикселя на экране (`GetDC(0)`), который отображает аддон-маркер. Не внедряется в `Wow.exe`, не читает память игры и не эмулирует нажатия клавиш или мыши.

### Быстрый старт
1. **Скачать**: Загрузите `AikoArenaNotifier.exe` со страницы [Последних релизов](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest).
2. **Аддон**: Установите аддон через [CurseForge](https://www.curseforge.com/wow/addons/aiko-arena-notifier) или [GitHub](https://github.com/aiko-tmpx/arena-notifier-addon) (или вручную в `Interface/AddOns/`). Проверьте работу командой `/aan test`.
3. **Запуск**: Запустите `AikoArenaNotifier.exe`, выберите монитор с игрой и нажмите **Start Monitoring**.

### Настройка Telegram
1. Получите **токен бота**: напишите [@BotFather](https://t.me/BotFather) (`/newbot`).
2. Узнайте свой **Chat ID**: напишите [@userinfobot](https://t.me/userinfobot) (нажмите Start).
3. **ВАЖНО**: Откройте своего созданного бота в Telegram и обязательно нажмите **СТАРТ** (или отправьте `/start`). Telegram запрещает ботам писать пользователям первыми.
4. Вставьте данные в программу, нажмите **Проверить Telegram** и нажмите кнопку **Start Monitoring** при вставании в очередь.

### Безопасность и античит
| Вектор проверки | Обычные боты / читы | AikoArenaNotifier | Статус |
| :--- | :--- | :--- | :--- |
| **Доступ к процессу** | `OpenProcess`, поиск дескрипторов и PID `Wow.exe` | Отсутствует. Программа не знает, запущена ли игра. | ✅ Безопасно |
| **Память процесса** | `ReadProcessMemory` / `WriteProcessMemory` | Ноль чтений памяти игры. | ✅ Безопасно |
| **Инжекты и хуки** | Хуки DirectX (`Present`/`EndScene`), внедрение DLL | Отсутствуют. Изолированный процесс Python. | ✅ Безопасно |
| **Эмуляция ввода** | `SendInput`, клики мышью для авто-приема | Отсутствует. Вы принимаете матч руками. | ✅ Безопасно |
| **Чтение экрана** | Хуки видеодрайвера игры | Стандартный Win32 GDI `GetDC(0)` (как в OBS или Discord). | ✅ Безопасно |
| **Внутриигровой аддон** | Небезопасные эксплойты Lua | Официальные события Blizzard (`UPDATE_BATTLEFIELD_STATUS`). | ✅ Безопасно |

---

<details>
<summary>Building from Source (Optional)</summary>

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --noconsole --name "AikoArenaNotifier" --icon="assets/icon.ico" --add-data="assets;assets" --collect-all customtkinter --clean main.py
```
</details>
