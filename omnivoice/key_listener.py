"""
OmniVoice - Global & In-Terminal Caps Lock / Hotkey Listener
Detects Caps Lock toggle via Linux evdev subsystem.
"""

import os
import sys
import select
import threading
from typing import Callable, List

class CapsLockListener:
    def __init__(self, on_toggle: Callable[[], None]):
        self.on_toggle = on_toggle
        self._stop_event = threading.Event()
        self._thread = None
        self._devices = []

    def _find_keyboards(self) -> list:
        try:
            import evdev
            keyboards = []
            for path in evdev.list_devices():
                try:
                    dev = evdev.InputDevice(path)
                    caps = dev.capabilities()
                    if evdev.ecodes.EV_KEY in caps:
                        keys = caps[evdev.ecodes.EV_KEY]
                        if evdev.ecodes.KEY_CAPSLOCK in keys:
                            keyboards.append(dev)
                except Exception:
                    pass
            return keyboards
        except Exception:
            return []

    def start(self):
        self._stop_event.clear()
        self._devices = self._find_keyboards()
        if not self._devices:
            return

        def worker():
            import evdev
            fds = {dev.fd: dev for dev in self._devices}
            while not self._stop_event.is_set():
                try:
                    r, _, _ = select.select(list(fds.keys()), [], [], 0.2)
                    for fd in r:
                        dev = fds[fd]
                        for event in dev.read():
                            if event.type == evdev.ecodes.EV_KEY:
                                if event.code == evdev.ecodes.KEY_CAPSLOCK and event.value == 1:
                                    # Key down event for Caps Lock
                                    self.on_toggle()
                except Exception:
                    pass

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        for dev in self._devices:
            try:
                dev.close()
            except Exception:
                pass
        self._devices = []
