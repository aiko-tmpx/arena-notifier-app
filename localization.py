"""Localization system for AikoArenaNotifier.
Supports English (en) and Russian (ru) with full UI and guide coverage.
"""

from __future__ import annotations

from typing import Dict, List

LOCALIZATION: Dict[str, Dict[str, str]] = {
    "en": {
        # App Header & Nav
        "app_title": "AikoArenaNotifier",
        "app_version": "v1.0.0",
        "tab_dashboard": "Dashboard",
        "tab_settings": "Settings",
        "tab_guide": "Guide / Help",
        
        # Persistent Status Footer
        "footer_status_label": "STATUS:",
        "status_idle": "IDLE",
        "status_scanning": "SCANNING",
        "footer_hotkey_prefix": "Hotkey:",
        
        # Dashboard Hero
        "hero_idle_title": "Scanner Paused",
        "hero_idle_subtitle": "Standing by for arena queue pop marker at screen (0, 0).",
        "hero_scanning_title": "Active Monitoring",
        "hero_scanning_subtitle": "Monitoring display presentation buffer for WoW queue pop marker.",
        
        # Dashboard Buttons & Diagnostics
        "btn_start_scan": "Start Monitoring ({hotkey})",
        "btn_stop_scan": "Stop Monitoring ({hotkey})",
        "diag_title": "Live Diagnostics",
        "diag_monitor": "Target Display:",
        "diag_pixel": "Sample Point: (X: 2, Y: 2)",
        "diag_current_rgb": "Current Read RGB:",
        "diag_swatch_label": "Live Color Preview",
        "metadata_summary": "Display: {display}  •  Hotkey: {hotkey}  •  Audio: {audio}",
        "audio_enabled": "Enabled",
        "audio_disabled": "Disabled",
        "log_title": "Recent Activity",
        "recent_activity_title": "Recent Activity",
        "no_recent_activity": "No recent events recorded.",
        "btn_clear_log": "Clear",
        
        # Dashboard Logs
        "log_app_ready": "AikoArenaNotifier initialized and ready.",
        "log_scanner_armed": "Scanner ARMED on display '{display}'. Monitoring pixel (2, 2)...",
        "log_scanner_stopped": "Scanner STOPPED. System is now IDLE.",
        "log_pop_detected": "🚨 ARENA QUEUE POP DETECTED! Color match confirmed.",
        "log_auto_stopped": "Auto-stopped scanner to prevent alert spam.",
        "log_telegram_sending": "Dispatching Telegram push notification...",
        "log_telegram_success": "Telegram notification successfully delivered!",
        "log_telegram_error": "Telegram notification failed: {error}",
        "log_telegram_skipped": "Telegram notification skipped: Bot Token or Chat ID not configured.",
        "log_sound_played": "Host audio alert tone played.",
        "log_settings_saved": "Settings successfully updated and saved.",
        "log_hotkey_bound": "Global hotkey registered: {hotkey}",
        "log_hotkey_error": "Failed to bind hotkey '{hotkey}'.",
        
        # Settings
        "settings_title": "Application Settings",
        "settings_tg_token_label": "Telegram Bot Token:",
        "settings_tg_token_placeholder": "e.g. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ",
        "settings_tg_chat_id_label": "Telegram Chat ID:",
        "settings_tg_chat_id_placeholder": "e.g. 987654321",
        "settings_display_label": "Target Game Display:",
        "settings_hotkey_label": "Toggle Hotkey:",
        "settings_sound_label": "Play audible alert on host PC when pop detected",
        "settings_test_tg_btn": "Test Telegram Connection",
        "settings_save_btn": "Save Settings",
        
        # Settings Status Feedback
        "status_token_empty": "Error: Telegram Bot Token cannot be empty.",
        "status_chat_id_empty": "Error: Telegram Chat ID cannot be empty.",
        "status_testing_connection": "Testing Telegram connection...",
        "status_test_success": "Success: Test notification delivered to Telegram!",
        "status_test_failed": "Error: Connection failed ({error})",
        "status_saved_success": "Settings saved successfully!",
        "status_saved_failed": "Error: Failed to write configuration file.",
        
        # Guide / Help
        "guide_title": "Setup & Usage Guide",
        "guide_lang_label": "Guide Language:",
        
        "guide_step1_title": "Step 1: Create a Telegram Bot",
        "guide_step1_body": (
            "1. Open Telegram and search for @BotFather.\n"
            "2. Send /start, then send /newbot.\n"
            "3. Choose a name and username for your bot (e.g. MyArenaNotifierBot).\n"
            "4. Copy the HTTP API token provided by BotFather into the Settings tab here."
        ),
        
        "guide_step2_title": "Step 2: Get Your Chat ID & Start the Bot",
        "guide_step2_body": (
            "1. CRITICAL: Open your newly created bot in Telegram and press START (or send /start).\n"
            "   (Bots cannot message you first until you start the conversation!)\n"
            "2. Search for @userinfobot in Telegram and press START.\n"
            "3. Copy your numeric Id (e.g. 123456789) into the Chat ID field in Settings.\n"
            "4. Click 'Test Telegram Connection' to verify you receive the test alert."
        ),
        
        "guide_step3_title": "Step 3: WoW Companion Addon",
        "guide_step3_body": (
            "1. The companion addon is located in your World of Warcraft AddOns directory:\n"
            "   World of Warcraft\\_retail_\\Interface\\AddOns\\AikoArenaNotifier\n"
            "2. When an arena, Solo Shuffle, or Battleground queue pops, the addon renders a 5x5 purple square at (0, 0).\n"
            "3. You can test the marker in-game at any time with the slash command:\n"
            "   /aan test\n"
            "4. Ensure your game is running on the monitor selected in the Settings tab."
        ),
        
        "guide_step4_title": "Step 4: Hotkey & Anti-Cheat Safety",
        "guide_step4_body": (
            "1. Press your configured hotkey (default F9) or click 'START SCANNING' when you queue up.\n"
            "2. When your queue pops, AikoArenaNotifier immediately pushes an alert to Telegram, sounds a beep, and AUTO-STOPS.\n"
            "3. After you finish your match and re-queue, simply press F9 again to re-arm.\n"
            "4. ZERO-TOLERANCE ANTI-CHEAT: The app never inspects or touches WoW.exe memory, processes, or inputs. It only passively reads screen pixels, exactly like OBS or Discord screen-share."
        ),
    },
    "ru": {
        # App Header & Nav
        "app_title": "AikoArenaNotifier",
        "app_version": "v1.0.0",
        "tab_dashboard": "Главная",
        "tab_settings": "Настройки",
        "tab_guide": "Инструкция / Помощь",
        
        # Persistent Status Footer
        "footer_status_label": "СТАТУС:",
        "status_idle": "ОЖИДАНИЕ",
        "status_scanning": "СКАНИРОВАНИЕ",
        "footer_hotkey_prefix": "Горячая клавиша:",
        
        # Dashboard Hero
        "hero_idle_title": "Сканер на паузе",
        "hero_idle_subtitle": "Ожидание появления индикатора очереди арены в координатах (0, 0).",
        "hero_scanning_title": "Активный мониторинг",
        "hero_scanning_subtitle": "Мониторинг буфера экрана для фиксации метки аддона WoW.",
        
        # Dashboard Buttons & Diagnostics
        "btn_start_scan": "Начать мониторинг ({hotkey})",
        "btn_stop_scan": "Остановить мониторинг ({hotkey})",
        "diag_title": "Диагностика в реальном времени",
        "diag_monitor": "Игровой монитор:",
        "diag_pixel": "Точка замера: (X: 2, Y: 2)",
        "diag_current_rgb": "Текущий RGB:",
        "diag_swatch_label": "Цвет пикселя",
        "metadata_summary": "Дисплей: {display}  •  Клавиша: {hotkey}  •  Звук: {audio}",
        "audio_enabled": "Вкл",
        "audio_disabled": "Выкл",
        "log_title": "История событий",
        "recent_activity_title": "История событий",
        "no_recent_activity": "Нет недавних событий.",
        "btn_clear_log": "Очистить",
        
        # Dashboard Logs
        "log_app_ready": "AikoArenaNotifier инициализирован и готов к работе.",
        "log_scanner_armed": "Сканер ВКЛЮЧЕН на дисплее '{display}'. Анализ пикселя (2, 2)...",
        "log_scanner_stopped": "Сканер ВЫКЛЮЧЕН. Режим ожидания.",
        "log_pop_detected": "🚨 ОЧЕРЕДЬ АРЕНЫ НАЙДЕНА! Совпадение цвета подтверждено.",
        "log_auto_stopped": "Сканер автоматически остановлен для предотвращения спама.",
        "log_telegram_sending": "Отправка push-уведомления в Telegram...",
        "log_telegram_success": "Уведомление в Telegram успешно доставлено!",
        "log_telegram_error": "Ошибка отправки в Telegram: {error}",
        "log_telegram_skipped": "Отправка в Telegram пропущена: Токен бота или Chat ID не настроены.",
        "log_sound_played": "Воспроизведен звуковой сигнал оповещения на ПК.",
        "log_settings_saved": "Настройки успешно сохранены.",
        "log_hotkey_bound": "Зарегистрирована горячая клавиша: {hotkey}",
        "log_hotkey_error": "Не удалось назначить горячую клавишу '{hotkey}'.",
        
        # Settings
        "settings_title": "Настройки приложения",
        "settings_tg_token_label": "Telegram Bot Token:",
        "settings_tg_token_placeholder": "например: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ",
        "settings_tg_chat_id_label": "Telegram Chat ID:",
        "settings_tg_chat_id_placeholder": "например: 987654321",
        "settings_display_label": "Монитор с запущенной игрой:",
        "settings_hotkey_label": "Горячая клавиша включения:",
        "settings_sound_label": "Звуковой сигнал на компьютере при нахождении очереди",
        "settings_test_tg_btn": "Проверить подключение Telegram",
        "settings_save_btn": "Сохранить настройки",
        
        # Settings Status Feedback
        "status_token_empty": "Ошибка: Токен бота Telegram не может быть пустым.",
        "status_chat_id_empty": "Ошибка: Telegram Chat ID не может быть пустым.",
        "status_testing_connection": "Проверка подключения к Telegram...",
        "status_test_success": "Успешно: Тестовое уведомление доставлено в Telegram!",
        "status_test_failed": "Ошибка: Сбой подключения ({error})",
        "status_saved_success": "Настройки успешно сохранены!",
        "status_saved_failed": "Ошибка: Не удалось записать файл конфигурации.",
        
        # Guide / Help
        "guide_title": "Инструкция по настройке и использованию",
        "guide_lang_label": "Язык инструкции:",
        
        "guide_step1_title": "Шаг 1: Создание Telegram бота",
        "guide_step1_body": (
            "1. Откройте Telegram и найдите бота @BotFather.\n"
            "2. Отправьте команду /start, затем /newbot.\n"
            "3. Укажите название и юзернейм для бота (например, MyArenaNotifierBot).\n"
            "4. Скопируйте полученный HTTP API токен во вкладку Настройки."
        ),
        
        "guide_step2_title": "Шаг 2: Получение Chat ID и запуск бота",
        "guide_step2_body": (
            "1. ВАЖНО: Откройте созданного бота в Telegram и нажмите СТАРТ (или отправьте /start).\n"
            "   (Боты не могут писать первыми, пока вы не запустите диалог!)\n"
            "2. Найдите в Telegram бота @userinfobot и нажмите СТАРТ.\n"
            "3. Скопируйте ваш числовой Id (например, 123456789) в поле Chat ID в Настройках.\n"
            "4. Нажмите 'Проверить подключение Telegram', чтобы убедиться в доставке уведомления."
        ),
        
        "guide_step3_title": "Шаг 3: Аддон для World of Warcraft",
        "guide_step3_body": (
            "1. Аддон AikoArenaNotifier находится в директории аддонов WoW:\n"
            "   World of Warcraft\\_retail_\\Interface\\AddOns\\AikoArenaNotifier\n"
            "2. При появлении подтверждения очереди аддон рисует квадрат 5x5 в верхнем левом углу (0, 0).\n"
            "3. Вы можете проверить отображение квадрата в игре в любой момент командой:\n"
            "   /aan test\n"
            "4. Убедитесь, что в Настройках выбран тот монитор, на котором запущена игра."
        ),
        
        "guide_step4_title": "Шаг 4: Горячие клавиши и безопасность античита",
        "guide_step4_body": (
            "1. Нажмите назначенную клавишу (по умолчанию F9) или кнопку 'НАЧАТЬ СКАНИРОВАНИЕ' при вставании в очередь.\n"
            "2. Когда очередь появится, AikoArenaNotifier моментально отправит уведомление в Telegram, подаст звуковой сигнал и АВТОМАТИЧЕСКИ ОСТАНОВИТСЯ.\n"
            "3. После завершения боя и повторного входа в очередь снова нажмите F9 для активации сканера.\n"
            "4. ПОЛНАЯ БЕЗОПАСНОСТЬ: Приложение никогда не взаимодействует с процессом Wow.exe, не читает память и не симулирует ввод клавиш/мыши. Оно лишь пассивно считывает пиксель рабочего стола, аналогично OBS или демонстрации экрана в Discord."
        ),
    },
}


def get_supported_languages() -> List[str]:
    """Returns list of supported language codes."""
    return list(LOCALIZATION.keys())


def t(key: str, lang: str = "en", **kwargs: str) -> str:
    """Retrieves localized string with formatting support and graceful fallback."""
    strings = LOCALIZATION.get(lang)
    if not strings:
        strings = LOCALIZATION["en"]

    text = strings.get(key)
    if text is None:
        text = LOCALIZATION["en"].get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text

    return text
