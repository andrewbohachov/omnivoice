"""
OmniVoice - Internationalization (i18n)
Supports English (default) and Russian. Zero emojis.
"""

STRINGS = {
    "en": {
        "title": "OmniVoice - Voice Prompting for Terminal AI Agents",
        "setup_title": "--- [ OmniVoice First-Run Setup ] ---",
        "setup_prompt": "Choose your speech recognition engine:",
        "opt_small": "1. Whisper Small (Recommended) - ~480 MB, 100% offline, balanced speed & code vocabulary",
        "opt_google": "2. Google Speech - 0 MB download, fast cloud API, zero RAM usage",
        "opt_turbo": "3. Whisper Turbo (Large-v3) - ~1.6 GB, maximum accuracy for high-end PCs",
        "setup_saved": "[OK] Configuration saved to {path}",
        "select_agent_title": "--- [ Select AI Agent to Launch ] ---",
        "listening": "\n[● REC] Listening... Speak your prompt now. Press Caps Lock again to stop.\n",
        "transcribing": "\n[*] Transcribing voice with {engine}...\n",
        "injected": "[OK] Injected {count} characters into prompt.\n",
        "error_recording": "[!] Audio recording error: {err}",
        "error_transcription": "[!] Transcription error: {err}",
        "help_header": "--- [ Interactive Controls ] ---",
        "caps_tip": "[INFO] Press [Caps Lock] to toggle voice recording on and off.",
        "config_updated": "[OK] Engine set to: {engine}",
        "engine_label": "Engine: {engine}",
        "agent_not_found": "[!] Warning: '{cmd}' is not found in PATH. Launching anyway...",
    },
    "ru": {
        "title": "OmniVoice - Голосовой ввод для терминальных AI-агентов",
        "setup_title": "--- [ Первоначальная настройка OmniVoice ] ---",
        "setup_prompt": "Выберите движок распознавания речи:",
        "opt_small": "1. Whisper Small (Рекомендуется) - ~480 МБ, 100% оффлайн, идеален для кода",
        "opt_google": "2. Google Speech - 0 МБ на диске, быстрый облачный API, 0 МБ ОЗУ",
        "opt_turbo": "3. Whisper Turbo (Large-v3) - ~1.6 ГБ, максимальная точность для мощных ПК",
        "setup_saved": "[OK] Настройки сохранены в {path}",
        "select_agent_title": "--- [ Выберите AI-агента для запуска ] ---",
        "listening": "\n[● REC] Идёт запись... Говорите ваш промпт. Нажмите Caps Lock повторно для завершения.\n",
        "transcribing": "\n[*] Расшифровка голоса через {engine}...\n",
        "injected": "[OK] Вставлено символов: {count}.\n",
        "error_recording": "[!] Ошибка записи звука: {err}",
        "error_transcription": "[!] Ошибка распознавания: {err}",
        "help_header": "--- [ Управление ] ---",
        "caps_tip": "[INFO] Нажмите [Caps Lock] для включения и выключения записи голоса.",
        "config_updated": "[OK] Установлен движок: {engine}",
        "engine_label": "Движок: {engine}",
        "agent_not_found": "[!] Внимание: '{cmd}' не найден в PATH. Попытка запуска...",
    }
}

class I18n:
    def __init__(self, lang: str = "en"):
        self.lang = "ru" if lang.lower().startswith("ru") else "en"

    def set_lang(self, lang: str):
        self.lang = "ru" if lang.lower().startswith("ru") else "en"

    def get(self, key: str, **kwargs) -> str:
        text = STRINGS.get(self.lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
        if kwargs:
            return text.format(**kwargs)
        return text

i18n = I18n("en")
