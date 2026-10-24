"""
OmniVoice - Faster-Whisper Local Engine
Offline, fast inference with CTranslate2. Supports small, large-v3-turbo, and base models.
"""

import numpy as np
from typing import Optional
from .base import BaseEngine
from ..punctuator import enhance_text

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

        device = "cpu"
        compute_type = "int8"

        # Check for working CUDA environment
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                try:
                    # Test if CUDA libraries (libcublas.so, libcudnn.so) actually load
                    test_m = WhisperModel(self.model_size, device="cuda", compute_type="float16")
                    dummy = np.zeros(16000, dtype=np.float32)
                    list(test_m.transcribe(dummy, language=self.language)[0])
                    self._model = test_m
                    self._device = "cuda"
                    self._compute_type = "float16"
                    return
                except Exception:
                    # Missing libcublas or CUDA library - fallback to CPU
                    device = "cpu"
                    compute_type = "int8"
        except Exception:
            device = "cpu"
            compute_type = "int8"

        self._device = device
        self._compute_type = compute_type
        self._model = WhisperModel(
            self.model_size,
            device=self._device,
            compute_type=self._compute_type
        )

    def transcribe(self, audio_np: np.ndarray, sample_rate: int = 16000) -> str:
        if len(audio_np) == 0:
            return ""

        self._ensure_model_loaded()

        # Resample / ensure float32
        audio_float32 = audio_np.astype(np.float32)

        # Transcribe directly from numpy array (bypassing pyav file reader)
        segments, info = self._model.transcribe(
            audio_float32,
            language=self.language,
            beam_size=5,
            vad_filter=False,
            initial_prompt="Unix, Linux, macOS, Windows, Git, GitHub, Pull Request, Push-to-Talk, bash, Python, Docker, Kubernetes, API, REST, JSON, Claude, Antigravity, Codex, Aider, Cursor, LLM, bugfix, deploy"
        )
        # Smart join segments ensuring periods between complete clauses
        joined = ""
        for seg in segments:
            s = seg.text.strip()
            if not s:
                continue
            if not joined:
                joined = s
            else:
                if s and s[0].isupper() and not joined.endswith((".", "!", "?", ":", ";", ",")):
                    joined += ". " + s
                else:
                    joined += " " + s

        return enhance_text(joined.strip())
