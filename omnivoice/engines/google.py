"""
OmniVoice - Google Speech Engine (Chromium STT API)
0 MB download, 0 MB RAM, free, no API keys required.
"""

import io
import wave
import numpy as np
import speech_recognition as sr
from .base import BaseEngine

class GoogleSpeechEngine(BaseEngine):
    def __init__(self, language: str = "ru-RU"):
        self.language = language
        self.recognizer = sr.Recognizer()

    @property
    def name(self) -> str:
        return "Google Speech"

    def transcribe(self, audio_np: np.ndarray, sample_rate: int = 16000) -> str:
        if len(audio_np) == 0:
            return ""

        # Convert float32 [-1.0, 1.0] to int16 PCM bytes
        int16_data = (np.clip(audio_np, -1.0, 1.0) * 32767.0).astype(np.int16)
        
        # Build in-memory WAV container
        wav_buf = io.BytesIO()
        with wave.open(wav_buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int16_data.tobytes())
        wav_buf.seek(0)

        with sr.AudioFile(wav_buf) as source:
            audio_data = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                return text.strip()
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                return f"[Error: {e}]"
