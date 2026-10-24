"""
OmniVoice - Audio Recorder
Captures 16kHz mono audio from default microphone using sounddevice or ffmpeg/arecord fallback.
"""

import threading
import numpy as np
from typing import List, Optional

class AudioRecorder:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self._chunks: List[np.ndarray] = []
        self._stream = None
        self._lock = threading.Lock()
        self._backend = "sounddevice"

        try:
            import sounddevice as sd
            self._sd = sd
        except Exception:
            self._sd = None
            self._backend = "ffmpeg"

    def start(self):
        with self._lock:
            self._chunks = []
            self.is_recording = True

            if self._sd is not None:
                try:
                    def callback(indata, frames, time_info, status):
                        if self.is_recording:
                            self._chunks.append(indata.copy())

                    self._stream = self._sd.InputStream(
                        samplerate=self.sample_rate,
                        channels=1,
                        dtype="float32",
                        callback=callback
                    )
                    self._stream.start()
                    return
                except Exception:
                    self._sd = None
                    self._backend = "ffmpeg"

            # Fallback to ffmpeg pulse capture if sounddevice fails
            self._start_ffmpeg()

    def _start_ffmpeg(self):
        import subprocess
        import tempfile
        self._tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        cmd = [
            "ffmpeg", "-f", "pulse", "-i", "default",
            "-ar", str(self.sample_rate), "-ac", "1",
            "-y", self._tmp_wav
        ]
        self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self) -> np.ndarray:
        with self._lock:
            self.is_recording = False

            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None

                if not self._chunks:
                    return np.array([], dtype=np.float32)
                return np.concatenate(self._chunks, axis=0).flatten()

            elif hasattr(self, "_proc") and self._proc is not None:
                import time
                import wave
                import os
                try:
                    self._proc.terminate()
                    self._proc.wait(timeout=1.0)
                except Exception:
                    self._proc.kill()
                self._proc = None

                time.sleep(0.1)
                if os.path.exists(self._tmp_wav):
                    try:
                        with wave.open(self._tmp_wav, 'rb') as w:
                            frames = w.readframes(w.getnframes())
                            arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                        os.remove(self._tmp_wav)
                        return arr
                    except Exception:
                        pass
                return np.array([], dtype=np.float32)

            return np.array([], dtype=np.float32)
