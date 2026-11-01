# AikoArenaNotifier

<div align="center">

**Lightweight, Ban-Safe Desktop Companion for World of Warcraft PvP Queue Notifications**

[ English ](#english) | [ Русский ](#русский)

</div>

---

<a name="english"></a>
## English

### 1. Overview & Value Proposition

**AikoArenaNotifier** is an ultra-lightweight, bloat-free desktop companion utility designed for competitive World of Warcraft (Retail) PvP players. While waiting in lengthy Arena or Solo Shuffle queues, you no longer need to remain anchored to your desk or monitor. 

The moment your queue pops, AikoArenaNotifier detects the in-game event and sends an instant push alert straight to your phone, smartwatch, or desktop via Telegram:

```text
🚨 QUEUE POPPED! 🚨
```

- **Zero Game Interaction**: Operates entirely outside the WoW process environment.
- **100% Ban-Safe**: Employs passive OS-level desktop pixel sampling (`GetDC(0)` + `GetPixel`).
- **Zero Synthetic Input**: The client never automates clicks or gameplay inputs. You walk up to your PC and click "Enter Battle" yourself.
- **Single-Window Utility**: Fixed compact layout (540x650), modern typography, instant auto-save, and bilingual interface (English / Русский).

---

### 2. Download & Quick Start

[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-7C3AED?style=for-the-badge&logo=windows)](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest)

#### Step 1: Install the Companion WoW Addon
The desktop application requires the companion World of Warcraft addon to render an unobtrusive pixel indicator when your queue pops.
- **CurseForge Addon Page**: [https://www.curseforge.com/wow/addons/aiko-arena-notifier](https://www.curseforge.com/wow/addons/aiko-arena-notifier)
- Alternatively, install manually by placing the addon folder into:
  ```text
  World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier
  ```

#### Step 2: In-Game Verification
Launch World of Warcraft and execute the following slash command in chat:
```text
/aan test
```
This temporarily displays a 5x5 pixel indicator at the top-left corner of your screen (`(0, 0)`) for 3 seconds to confirm the addon is active.

#### Step 3: Run the Desktop Companion
Download and launch [`AikoArenaNotifier.exe`](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest). No installation is required.

---

### 3. Telegram Bot Setup (BYOB — Bring Your Own Bot)

AikoArenaNotifier follows the **BYOB** principle: you create your own private Telegram bot. Your API token and chat credentials remain exclusively on your computer; no external proxy, web service, or third-party server ever touches your data.

```
┌──────────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│   @BotFather     │ ───>  │  AikoArenaNotifier   │ ───>  │   Your Phone /   │
│  (API Token)     │       │   Desktop Client     │       │    Smartwatch    │
├──────────────────┤       │  (Local Auto-Save)   │       └──────────────────┘
│  @userinfobot    │ ───>  │                      │
│   (Chat ID)      │       └──────────────────────┘
└──────────────────┘
```

#### Step-by-Step Instructions:

1. **Obtain Bot Token via [@BotFather](https://t.me/BotFather)**:
   - In Telegram, search for [@BotFather](https://t.me/BotFather) and send `/newbot`.
   - Choose a display name (e.g., `My Queue Notifier`) and a unique username ending in `bot` (e.g., `my_arena_queue_bot`).
   - Copy the HTTP API token provided by BotFather (formatted as `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

2. **Obtain Your Telegram Chat ID**:
   - In Telegram, open [@userinfobot](https://t.me/userinfobot) (or [@getmyid_bot](https://t.me/getmyid_bot)) and press **Start**.
   - Copy the numeric `Id` (e.g., `987654321`).

3. **Authorize Your Bot (CRITICAL STEP)**:
   > [!IMPORTANT]
   > Under Telegram's strict anti-spam privacy policy, **bots cannot send messages to a user until that user initiates a chat with the bot**.
   > 
   > Open Telegram, search for your newly created bot username, and press **START** (or send `/start`). If you skip this step, Telegram will reject all notification dispatches with an `HTTP 403 Forbidden` error.

4. **Configure the Desktop App**:
   - Paste your **Bot Token** into the *Telegram Bot Token* field.
   - Paste your **Chat ID** into the *Telegram Chat ID* field.
   - Use the lock button (`🔒` / `🔓`) next to each input to protect against accidental edits.
   - Click **Test Telegram Connection**. You will receive an immediate confirmation message:
     ```text
     🔔 AikoArenaNotifier: Connection verified!
     ```
   - All settings auto-save seamlessly to `config.json`.

---

### 4. Workflow & Daily Use

```
 1. Queue Up In-Game (Arena / Solo Shuffle)
               │
               ▼
 2. Press Hotkey (F9 / F12) to Start Monitoring
               │
               ▼
 3. Go AFK / Relax Away from Desk
               │
               ▼
 4. Queue Pops ──> 5x5 Indicator Appears ──> Instant Desktop Detection
               │
               ▼
 5. Push Notification Sent: "🚨 QUEUE POPPED! 🚨" + PC Audio Alert
               │
               ▼
 6. Monitoring Auto-Stops (prevents duplicate spam / rate-limits)
               │
               ▼
 7. Walk to PC & Click "Enter Battle" Manually
```

1. **Target Display**: Select the monitor running World of Warcraft from the *Target Game Display* dropdown.
2. **Hotkey**: Choose your preferred global hotkey (`F8`, `F9`, `F10`, `F11`, or `F12`).
3. **Queue & Arm**: When entering the queue, hit your hotkey. The status turns green (`Scanning for queue marker...`).
4. **Instant Pop**: When the queue pops, your phone receives `🚨 QUEUE POPPED! 🚨`, and a local chime plays.
5. **Auto-Stop**: The scanner immediately disarms upon detection to protect against Telegram rate-limits.
6. **Accept**: Return to your desk and manually click the "Enter Battle" button.

---

### 5. Anti-Cheat & Safety Breakdown (Why It's 100% Safe)

Blizzard's **Warden** anti-cheat actively monitors process space, API hooking, thread creation, DLL injection, and memory integrity of the game client. AikoArenaNotifier is architected specifically to sit entirely outside Warden's surveillance scope:

| Attack Vector / Monitored Area | Conventional Cheat / Bot Behavior | AikoArenaNotifier Architecture | Warden Status |
| :--- | :--- | :--- | :--- |
| **Process Inspection** | Calls `OpenProcess`, inspects handles, enumerates `Wow.exe` PID | **ZERO** process enumeration. The app does not know or care if `Wow.exe` is running. | ✅ Untouched |
| **Process Memory** | Calls `ReadProcessMemory`, `WriteProcessMemory`, scan offsets | **ZERO** memory reads. Does not touch RAM allocated to any game executable. | ✅ Untouched |
| **Code / DLL Injection** | Calls `VirtualAllocEx`, `CreateRemoteThread`, injects DLLs | **ZERO** injection. Runs strictly inside its own isolated Python runtime. | ✅ Untouched |
| **Graphics Hooking** | Hooks DirectX (`EndScene`/`Present`), Vulkan, or OpenGL | **ZERO** pipeline hooking. No overlay hooks or graphics driver tampering. | ✅ Untouched |
| **Gameplay Input Emulation** | Calls `SendInput`, `PostMessage`, synthetic mouse clicks to auto-accept | **STRICTLY PASSIVE**. Never sends keystrokes or mouse events into the game window. | ✅ Untouched |
| **Screen Reading Method** | Injects D3D hooks or reads proprietary DirectX framebuffers | Passive Windows Desktop GDI `GetDC(0)` + `GetPixel`. Identical to OBS Studio, Discord, or Windows Snipping Tool. | ✅ Untouched |
| **In-Game Mechanism** | Unsafe Lua memory exploits or protected functions | Uses Blizzard's documented, public UI events (`UPDATE_BATTLEFIELD_STATUS`, `LFG_PROPOSAL_SHOW`). | ✅ 100% Legal Lua API |

> [!NOTE]
> From the operating system's perspective, AikoArenaNotifier's desktop pixel sampling is indistinguishable from standard desktop utilities such as OBS Studio, Discord screen sharing, or an artist's digital color picker.

---

### 6. Building from Source

#### Prerequisites
- Windows 10 / 11 (64-bit)
- Python 3.10 or higher
- Git

#### Installation Steps

```powershell
# 1. Clone the repository
git clone https://github.com/aiko-tmpx/arena-notifier-app.git
cd arena-notifier-app

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Run tests to verify environment
python -m pytest

# 5. Launch application from source
python main.py
```

#### Compiling Standalone Executable (`.exe`)

Compile a zero-console, single-file Windows executable with icon assets bundled:

```powershell
pyinstaller --noconfirm --onefile --noconsole --name AikoArenaNotifier --icon=assets/icon.ico --add-data="assets;assets" --collect-all customtkinter --clean main.py
```
Or execute the automated build script:
```powershell
.\build_exe.bat
```
The resulting binary will be created at `dist\AikoArenaNotifier.exe`.

---

<a name="русский"></a>
## Русский

### 1. Обзор и преимущества

**AikoArenaNotifier** — это легковесный настольный компаньон без лишнего мусора для активных PvP-игроков World of Warcraft (Retail). Во время ожидания долгой очереди на Арену или Solo Shuffle вам больше не нужно сидеть привязанным к монитору.

В тот самый момент, когда очередь прокнет, утилита мгновенно зафиксирует появление приглашения и отправит push-уведомление прямо на ваш телефон или смарт-часы через Telegram:

```text
🚨 QUEUE POPPED! 🚨
```

- **Полное отсутствие взаимодействия с процессом игры**: Работает исключительно на уровне рабочего стола Windows.
- **100% Защита от бана**: Пассивное считывание цвета экранного пикселя через стандартный системный интерфейс Windows GDI (`GetDC(0)` + `GetPixel`).
- **Никакой автоматизации**: Программа не нажимает кнопки за вас. Вы получаете уведомление на телефон, подходите к компьютеру и сами подтверждаете вход в бой.
- **Удобный компактный интерфейс**: Фиксированное аккуратное окно (540x650), современная типографика Inter, мгновенное автосохранение настроек и поддержка русского и английского языков.

---

### 2. Загрузка и быстрый старт

[![Скачать последний релиз](https://img.shields.io/badge/Скачать-Последний%20Релиз-7C3AED?style=for-the-badge&logo=windows)](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest)

#### Шаг 1: Установка аддона для World of Warcraft
Для работы настольной программы необходим компактный аддон-индикатор:
- **Страница аддона на CurseForge**: [https://www.curseforge.com/wow/addons/aiko-arena-notifier](https://www.curseforge.com/wow/addons/aiko-arena-notifier)
- Либо установите вручную, скопировав папку аддона в:
  ```text
  World of Warcraft\_retail_\Interface\AddOns\AikoArenaNotifier
  ```

#### Шаг 2: Проверка работы аддона в игре
Зайдите в World of Warcraft и введите в чат команду:
```text
/aan test
```
В левом верхнем углу экрана (`(0, 0)`) на 3 секунды появится тестовый квадрат 5x5 пикселей. Это подтверждает, что аддон активен и готов к работе.

#### Шаг 3: Запуск настольной программы
Скачайте и запустите исполняемый файл [`AikoArenaNotifier.exe`](https://github.com/aiko-tmpx/arena-notifier-app/releases/latest). Установка в систему не требуется.

---

### 3. Настройка Telegram-бота (BYOB — Свой собственный бот)

AikoArenaNotifier работает по принципу **BYOB** (Bring Your Own Bot): вы создаете своего личного приватного бота в Telegram. Токен и Chat ID хранятся исключительно локально на вашем ПК в файле `config.json`. Никаких сторонних серверов, веб-сервисов или посредников.

```
┌──────────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│   @BotFather     │ ───>  │  AikoArenaNotifier   │ ───>  │  Ваш смартфон /  │
│  (API Токен)     │       │ Настольный клиент    │       │   Смарт-часы     │
├──────────────────┤       │(Локальное авто-сохр.)│       └──────────────────┘
│  @userinfobot    │ ───>  │                      │
│   (Chat ID)      │       └──────────────────────┘
└──────────────────┘
```

#### Пошаговая инструкция:

1. **Создание бота через [@BotFather](https://t.me/BotFather)**:
   - В Telegram найдите официального бота [@BotFather](https://t.me/BotFather) и отправьте команду `/newbot`.
   - Задайте имя (например, `Arena Alert`) и уникальный юзернейм, оканчивающийся на `bot` (например, `my_wow_queue_bot`).
   - Скопируйте полученный HTTP API токен (вид: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

2. **Получение вашего Telegram Chat ID**:
   - Откройте бота [@userinfobot](https://t.me/userinfobot) (или [@getmyid_bot](https://t.me/getmyid_bot)) и нажмите **Start**.
   - Скопируйте числовое значение `Id` (например, `987654321`).

3. **Активация вашего бота (КРИТИЧЕСКИ ВАЖНЫЙ ШАГ)**:
   > [!IMPORTANT]
   > Согласно политике безопасности и защиты от спама Telegram, **боты не могут писать пользователю первыми, пока пользователь сам не откроет диалог**.
   > 
   > Найдите в Telegram своего созданного бота по его юзернейму и обязательно нажмите кнопку **СТАРТ** (или отправьте `/start`). Если этого не сделать, Telegram отклонит отправку уведомления с ошибкой `HTTP 403 Forbidden`.

4. **Ввод данных в программу**:
   - Вставьте токен в поле *Токен Telegram-бота*.
   - Вставьте ваш Chat ID в поле *Telegram Chat ID*.
   - Нажмите иконку замка (`🔒` / `🔓`), чтобы заблокировать поля от случайного изменения.
   - Нажмите кнопку **Проверить Telegram**. На ваш телефон мгновенно придет тестовое сообщение:
     ```text
     🔔 AikoArenaNotifier: Connection verified!
     ```
   - Настройки автоматически сохраняются на диск.

---

### 4. Рабочий процесс и ежедневное использование

```
 1. Встаньте в очередь на Арену или Solo Shuffle в игре
                        │
                        ▼
 2. Нажмите горячую клавишу (F9 / F12) для старта мониторинга
                        │
                        ▼
 3. Спокойно отойдите от компьютера / займитесь своими делами
                        │
                        ▼
 4. Очередь находит матч ──> Появляется маркер ──> Мгновенный захват пикселя
                        │
                        ▼
 5. Приходит push-уведомление: "🚨 QUEUE POPPED! 🚨" + звуковой сигнал на ПК
                        │
                        ▼
 6. Мониторинг автоматически останавливается
                        │
                        ▼
 7. Вы подходите к ПК и сами кликаете "Войти в бой"
```

1. **Выбор монитора**: В выпадающем списке выберите монитор, на котором запущен World of Warcraft.
2. **Горячая клавиша**: Выберите удобную клавишу (`F8`, `F9`, `F10`, `F11`, `F12`).
3. **Поиск матча**: Встав в очередь, нажмите горячую клавишу. Статус станет зеленым (`Идет мониторинг...`).
4. **Оповещение**: При появлении приглашения на экран вы получите push-уведомление `🚨 QUEUE POPPED! 🚨` в Telegram, а из колонок ПК прозвучит звуковой сигнал.
5. **Авто-остановка**: После обнаружения маркерного пикселя сканирование сразу отключается, предотвращая спам и лимиты Telegram API.
6. **Принятие матча**: Подойдите к компьютеру и физически нажмите кнопку входа в игру.

---

### 5. Разбор защиты от античита (Почему бан на 100% исключен)

Античит Blizzard **Warden** строго отслеживает адресное пространство процессов, вызовы перехвата API (хуки), внедрение чужих DLL и эмуляцию устройств ввода. Архитектура AikoArenaNotifier полностью исключает возможность детекта:

| Вектор проверки античитом | Поведение читов / автоматизаторов | Архитектура AikoArenaNotifier | Статус безопасности |
| :--- | :--- | :--- | :--- |
| **Доступ к процессу игры** | Вызывает `OpenProcess`, получает хэндлы, ищет PID `Wow.exe` | **НОЛЬ** обращений к процессу. Программа даже не знает, запущена ли игра. | ✅ Безопасно |
| **Память процесса** | Вызывает `ReadProcessMemory` / `WriteProcessMemory`, ищет оффсеты | **НОЛЬ** чтений памяти. Ни один байт оперативной памяти WoW не читается. | ✅ Безопасно |
| **Инжекты и потоки** | Вызывает `VirtualAllocEx`, `CreateRemoteThread`, внедряет DLL | **НОЛЬ** инжектов. Код выполняется только внутри собственного процесса Python. | ✅ Безопасно |
| **Графические хуки** | Перехватывает кадры через хуки DirectX (`Present`/`EndScene`), Vulkan | **НОЛЬ** вмешательств в рендеринг. Графический пайплайн игры не затрагивается. | ✅ Безопасно |
| **Эмуляция ввода** | Вызывает `SendInput`, `mouse_event`, кликает кнопку входа | **СТРОГО ПАССИВНО**. В систему не отправляется никаких виртуальных кликов или нажатий клавиш. | ✅ Безопасно |
| **Чтение пикселя экрана** | Читает через инжект в графический драйвер игры | Пассивное чтение экранного буфера Windows через `GetDC(0)` + `GetPixel`. Неотличимо от OBS Studio, Discord или "Ножниц" Windows. | ✅ Безопасно |
| **Внутриигровой аддон** | Небезопасные эксплойты Lua, защищенные функции | Работает исключительно через легальный Blizzard Lua API (`UPDATE_BATTLEFIELD_STATUS`, `LFG_PROPOSAL_SHOW`). | ✅ Легально |

> [!NOTE]
> С точки зрения операционной системы Windows, чтение системного пикселя утилитой AikoArenaNotifier ничем не отличается от захвата экрана стриминговой программой OBS Studio, демонстрации экрана в Discord или работы пипетки выбора цвета в графическом редакторе.

---

### 6. Сборка из исходников

#### Системные требования
- Windows 10 / 11 (64-бит)
- Python 3.10 или новее
- Git

#### Пошаговая сборка

```powershell
# 1. Клонирование репозитория
git clone https://github.com/aiko-tmpx/arena-notifier-app.git
cd arena-notifier-app

# 2. Создание и активация виртуального окружения
python -m venv .venv
.\.venv\Scripts\activate

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Запуск автоматических тестов
python -m pytest

# 5. Запуск приложения из исходного кода
python main.py
```

#### Компиляция в один `.exe` файл

Для сборки автономного бинарного файла без открытия консоли:

```powershell
pyinstaller --noconfirm --onefile --noconsole --name AikoArenaNotifier --icon=assets/icon.ico --add-data="assets;assets" --collect-all customtkinter --clean main.py
```
Либо запустите готовый скрипт сборки:
```powershell
.\build_exe.bat
```
Готовый файл появится в каталоге `dist\AikoArenaNotifier.exe`.

---

### Лицензия / License

Distributed under the MIT License. Designed with zero anti-cheat footprint for competitive World of Warcraft PvP players.
