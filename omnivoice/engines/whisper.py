"""
OmniVoice - Faster-Whisper Local Engine
Offline, fast inference with CTranslate2. Supports small, large-v3-turbo, and base models.
"""

import numpy as np
from typing import Optional
from .base import BaseEngine

class FasterWhisperEngine(BaseEngine):
    def __init__(self, model_size: str = "small", language: str = "ru"):
        self.model_size = model_size
        self.language = language
        self._model = None
        self._device = "cpu"
        self._compute_type = "int8"

    @property
    def name(self) -> str:
        return f"Whisper {self.model_size.capitalize()}"

    def _ensure_model_loaded(self):
        if self._model is not None:
            return

        from faster_whisper import WhisperModel
        import shutil

        # Check for CUDA availability
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                self._device = "cuda"
                self._compute_type = "float16"
        except Exception:
            self._device = "cpu"
            self._compute_type = "int8"

        self._model = WhisperModel(
            self.model_size,
            device=self._device,
            compute_type=self._compute_type
        )

    def transcribe(self, audio_np: np.ndarray, sample_rate: int = 16000) -> str:
        if len(audio_np) == 0:
            return ""

        self._ensure_model_loaded()

        # Resample if not 16000
        audio_float32 = audio_np.astype(np.float32)

        # Transcribe directly from numpy array (bypassing pyav file reader)
        segments, info = self._model.transcribe(
            audio_float32,
            language=self.language,
            beam_size=5,
            vad_filter=True,
            initial_prompt="Linux, Git, bash, terminal, Python, Docker, API, FastAPI, Redis, pull request, bugfix, Claude, Antigravity, Codex"
        )
        text = " ".join([seg.text.strip() for seg in segments])
        return text.strip()
