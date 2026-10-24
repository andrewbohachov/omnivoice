"""
OmniVoice Engines Registry
"""

from .base import BaseEngine
from .google import GoogleSpeechEngine
from .whisper import FasterWhisperEngine

def get_engine(engine_name: str, language: str = "ru") -> BaseEngine:
    norm = engine_name.lower().replace("_", "-")
    lang_code = "ru" if language.startswith("ru") else "en"

    if "google" in norm:
        return GoogleSpeechEngine(language="ru-RU" if lang_code == "ru" else "en-US")
    elif "turbo" in norm:
        return FasterWhisperEngine(model_size="large-v3-turbo", language=lang_code)
    elif "base" in norm:
        return FasterWhisperEngine(model_size="base", language=lang_code)
    else:
        # Default: whisper-small
        return FasterWhisperEngine(model_size="small", language=lang_code)
