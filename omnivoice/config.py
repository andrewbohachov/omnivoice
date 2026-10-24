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
    Clean, in-place terminal arrow-key menu.
    Uses relative cursor movements (ESC [ N A) and line clears (ESC [ 2 K)
    to overwrite the menu in-place without duplicating lines.
    """
    import termios
    import tty
    import shutil

    selected = default_index
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    # Hide cursor
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

    first_draw = True
    rendered_line_count = 0

    def draw():
        nonlocal first_draw, rendered_line_count

        lines = [
            f"\x1b[1;37m{title}\x1b[0m",
            ""
        ]
        for i, opt in enumerate(options):
            marker = "[●]" if i == selected else "[ ]"
            color = "\x1b[1;36m" if i == selected else "\x1b[90m"
            lines.append(f"  {color}{marker} {opt}\x1b[0m")
        lines.append("")
        lines.append("\x1b[90m(Use [Up/Down] arrows, [j/k], or [1-9] to choose, [Enter] to confirm)\x1b[0m")

        # If not the first render, move cursor back up to the top of the menu
        if not first_draw and rendered_line_count > 0:
            sys.stdout.write(f"\x1b[{rendered_line_count}A\r")

        # Overwrite each line cleanly
        for l in lines:
            sys.stdout.write(f"\x1b[2K\r{l}\n")
        sys.stdout.flush()

        rendered_line_count = len(lines)
        first_draw = False

    try:
        tty.setraw(fd)
        draw()
        while True:
            char = sys.stdin.read(1)
            if char == '\x1b':
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    next2 = sys.stdin.read(1)
                    if next2 == 'A':  # Up
                        selected = (selected - 1) % len(options)
                    elif next2 == 'B':  # Down
                        selected = (selected + 1) % len(options)
            elif char in ('k', 'K'):  # Vim up
                selected = (selected - 1) % len(options)
            elif char in ('j', 'J'):  # Vim down
                selected = (selected + 1) % len(options)
            elif char.isdigit():
                num = int(char)
                if 1 <= num <= len(options):
                    selected = num - 1
            elif char in ('\r', '\n', ' '):
                break
            elif char == '\x03':  # Ctrl+C
                sys.stdout.write("\x1b[?25h\r\n")
                sys.stdout.flush()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                sys.exit(0)

            draw()
    finally:
        sys.stdout.write("\x1b[?25h\r\n")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return selected

def interactive_setup(lang: Optional[str] = None) -> Dict[str, Any]:
    if lang:
        i18n.set_lang(lang)
    
    cfg = load_config()

    print("==========================================================")
    print(f"       {i18n.get('setup_title')}")
    print("==========================================================")

    options = [
        "Whisper Small (Recommended) [~480 MB, 100% offline, balanced]",
        "Google Speech                [0 MB download, fast cloud API]",
        "Whisper Turbo (Large-v3)     [~1.6 GB, maximum accuracy]"
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
    print(f"[OK] Engine active: {chosen_engine}\n")
    return cfg
