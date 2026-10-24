"""
OmniVoice - Base Speech-to-Text Engine Interface
"""

import abc
import numpy as np

class BaseEngine(abc.ABC):
    @abc.abstractmethod
    def transcribe(self, audio_np: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribes a 1D float32 numpy array into text.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass
