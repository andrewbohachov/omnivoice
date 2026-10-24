"""
OmniVoice - Interactive PTY Wrapper
Wraps any terminal AI agent (agy, claude, codex, bash) in a transparent pseudoterminal.
Injects transcribed voice text directly into the agent's input stream upon Caps Lock toggle.
Zero emojis.
"""

import os
import sys
import pty
import tty
import fcntl
import signal
import termios
import struct
import select
import threading
from typing import List, Optional
from .audio import AudioRecorder
from .key_listener import CapsLockListener
from .engines import BaseEngine
from .i18n import i18n

class PtyWrapper:
    def __init__(self, command: List[str], engine: BaseEngine):
        self.command = command
        self.engine = engine
        self.recorder = AudioRecorder(sample_rate=16000)
        self.is_recording = False
        self.master_fd = None
        self._key_listener = None
        self._lock = threading.Lock()

    def _set_window_size(self):
        """Propagates terminal window size to slave PTY."""
        if self.master_fd is None:
            return
        try:
            buf = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, buf)
        except Exception:
            pass

    def _on_toggle(self):
        """Called whenever Caps Lock (or fallback key) is pressed."""
        if self.master_fd is None:
            return

        with self._lock:
            if not self.is_recording:
                # START RECORDING
                self.is_recording = True
                self.recorder.start()
                # Update window title & display subtle inline indicator without line break
                title_seq = f"\x1b]0;{i18n.get('listening_badge')} OmniVoice - Listening...\x07"
                inline_seq = f"\x1b7 \x1b[1;33m{i18n.get('listening_badge')}\x1b[0m"
                os.write(sys.stdout.fileno(), (title_seq + inline_seq).encode("utf-8"))
            else:
                # STOP RECORDING & TRANSCRIBE
                self.is_recording = False
                title_seq = f"\x1b]0;{i18n.get('transcribing_badge')} OmniVoice - Transcribing...\x07"
                inline_seq = f"\x1b8\x1b[K\x1b7 \x1b[1;36m{i18n.get('transcribing_badge')}\x1b[0m"
                os.write(sys.stdout.fileno(), (title_seq + inline_seq).encode("utf-8"))

                audio = self.recorder.stop()
                try:
                    if len(audio) > 0:
                        text = self.engine.transcribe(audio, sample_rate=16000)
                        if text:
                            # Clean up inline badge and restore title
                            cleanup = b"\x1b8\x1b[K\x1b]0;OmniVoice\x07"
                            os.write(sys.stdout.fileno(), cleanup)
                            # Inject recognized text directly into agent prompt
                            os.write(self.master_fd, text.encode("utf-8"))
                            return
                except Exception as e:
                    cleanup = b"\x1b8\x1b[K\x1b]0;OmniVoice\x07"
                    os.write(sys.stdout.fileno(), cleanup)
                    err_msg = f"\r\n\x1b[1;31m{i18n.get('error_transcription', err=e)}\x1b[0m\r\n"
                    os.write(sys.stdout.fileno(), err_msg.encode("utf-8"))
                    return

                # If no text recognized, clean up indicator
                cleanup = b"\x1b8\x1b[K\x1b]0;OmniVoice\x07"
                os.write(sys.stdout.fileno(), cleanup)

    def run(self) -> int:
        pid, self.master_fd = pty.fork()

        if pid == 0:
            # Child process: execute the requested agent
            try:
                os.execvp(self.command[0], self.command)
            except Exception as e:
                print(f"[!] Failed to execute '{self.command[0]}': {e}")
                sys.exit(1)

        # Parent process: handle I/O and voice injection
        self._set_window_size()

        # Handle SIGWINCH (terminal resize)
        def handle_sigwinch(signum, frame):
            self._set_window_size()
        signal.signal(signal.SIGWINCH, handle_sigwinch)

        # Save old terminal attributes and switch to raw mode
        old_tty = termios.tcgetattr(sys.stdin.fileno())

        # Start Caps Lock event listener
        self._key_listener = CapsLockListener(on_toggle=self._on_toggle)
        self._key_listener.start()

        # Warm up speech recognition engine in background
        def warmup():
            try:
                if hasattr(self.engine, "_ensure_model_loaded"):
                    self.engine._ensure_model_loaded()
            except Exception:
                pass
        threading.Thread(target=warmup, daemon=True).start()

        # Print initial tip
        sys.stdout.write(f"\x1b[90m{i18n.get('caps_tip')}\x1b[0m\r\n")
        sys.stdout.flush()

        try:
            tty.setraw(sys.stdin.fileno())

            while True:
                r, _, _ = select.select([sys.stdin.fileno(), self.master_fd], [], [])

                if sys.stdin.fileno() in r:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    
                    # Check for fallback hotkey in terminal (F6 = \x1b[17~ or Ctrl+Space = \x00)
                    if data in (b"\x00", b"\x1b[17~"):
                        self._on_toggle()
                    else:
                        os.write(self.master_fd, data)

                if self.master_fd in r:
                    try:
                        data = os.read(self.master_fd, 1024)
                    except OSError:
                        # Child has exited
                        break
                    if not data:
                        break
                    os.write(sys.stdout.fileno(), data)

        finally:
            self._key_listener.stop()
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_tty)

        _, status = os.waitpid(pid, 0)
        return os.waitstatus_to_exitcode(status)
