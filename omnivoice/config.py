"""
OmniVoice - Configuration Manager & Interactive Setup Wizard
Zero emojis.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .i18n import i18n

CONFIG_DIR = Path.home() / ".config" / "omnivoice"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "engine": "whisper-small",  # "whisper-small", "google", "whisper-turbo"
    "language": "ru",
    "hotkey": "caps_lock",
    "sound_feedback": True
}

def get_config_path() -> Path:
    return CONFIG_FILE

def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(data)
            return cfg
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(cfg: Dict[str, Any]):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def is_first_run() -> bool:
    return not CONFIG_FILE.exists()

def select_with_arrows(title: str, options: list, default_index: int = 0) -> int:
    """
    Simple, pure-Python terminal arrow-key menu without heavy external dependencies.
    """
    import termios
    import tty

    selected = default_index
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def draw_menu():
        # Clear lines
        sys.stdout.write("\r\x1b[K")
        sys.stdout.write(f"\n{title}\n\n")
        for i, opt in enumerate(options):
            marker = "[●]" if i == selected else "[ ]"
            color = "\x1b[36m" if i == selected else "\x1b[90m"
            sys.stdout.write(f"  {color}{marker} {opt}\x1b[0m\n")
        sys.stdout.write("\nUse [Up/Down] arrows to choose, [Enter] to confirm.\n")
        sys.stdout.flush()

    try:
        tty.setraw(fd)
        draw_menu()
        while True:
            char = sys.stdin.read(1)
            if char == '\x1b':
                # Escape sequence
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    next2 = sys.stdin.read(1)
                    if next2 == 'A':  # Up
                        selected = (selected - 1) % len(options)
                    elif next2 == 'B':  # Down
                        selected = (selected + 1) % len(options)
            elif char in ('\r', '\n'):
                break
            elif char == '\x03':  # Ctrl+C
                sys.exit(0)
            
            # Redraw
            lines_to_clear = len(options) + 5
            sys.stdout.write(f"\x1b[{lines_to_clear}A")
            draw_menu()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print()

    return selected

def interactive_setup(lang: Optional[str] = None) -> Dict[str, Any]:
    if lang:
        i18n.set_lang(lang)
    
    cfg = load_config()

    print("==========================================================")
    print(f"       {i18n.get('setup_title')}")
    print("==========================================================")

    options = [
        "Whisper Small (Recommended) - ~480 MB, 100% offline, balanced speed & code accuracy",
        "Google Speech - 0 MB download, fast cloud API, zero RAM usage",
        "Whisper Turbo (Large-v3) - ~1.6 GB, maximum accuracy for high-end PCs"
    ]
    engine_keys = ["whisper-small", "google", "whisper-turbo"]

    default_idx = 0
    if cfg.get("engine") in engine_keys:
        default_idx = engine_keys.index(cfg["engine"])

    idx = select_with_arrows(i18n.get("setup_prompt"), options, default_index=default_idx)
    chosen_engine = engine_keys[idx]
    cfg["engine"] = chosen_engine
    save_config(cfg)

    print(i18n.get("setup_saved", path=str(CONFIG_FILE)))
    print(f"Engine selected: {chosen_engine}\n")
    return cfg
