"""
OmniVoice CLI Entry Point
Handles argument parsing, first-run setup wizard, agent selection, and PTY launching.
Zero emojis.
"""

import os
import sys
import shutil
import argparse
from typing import List
from .config import load_config, save_config, is_first_run, interactive_setup, select_with_arrows
from .engines import get_engine
from .pty_wrapper import PtyWrapper
from .i18n import i18n

KNOWN_AGENTS = [
    ("Antigravity CLI (agy)", "agy"),
    ("Claude Code (claude)", "claude"),
    ("Codex CLI (codex)", "codex"),
    ("Aider (aider)", "aider"),
    ("Default Shell (bash)", "bash"),
]

def parse_args():
    parser = argparse.ArgumentParser(
        prog="omnivoice",
        description="OmniVoice: Voice Prompting & Dictation for Terminal AI Agents (Antigravity, Claude, Codex, Aider)."
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="Target AI agent or command to run (e.g. 'agy', 'claude', 'codex', 'bash')"
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        choices=["small", "google", "turbo", "whisper-small", "whisper-turbo"],
        help="Speech-to-text engine override (small, google, turbo)"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        choices=["en", "ru"],
        help="Interface language (en or ru)"
    )
    parser.add_argument(
        "--setup", "--config",
        action="store_true",
        help="Launch interactive setup wizard to change engine"
    )
    return parser.parse_args()

def choose_agent_interactively() -> List[str]:
    options = [label for label, cmd in KNOWN_AGENTS] + ["Custom command..."]
    idx = select_with_arrows("Select AI agent to launch with voice prompting:", options, default_index=0)
    
    if idx < len(KNOWN_AGENTS):
        cmd_name = KNOWN_AGENTS[idx][1]
        return [cmd_name]
    else:
        sys.stdout.write("Enter command to run: ")
        sys.stdout.flush()
        custom = sys.stdin.readline().strip()
        if not custom:
            return ["bash"]
        return custom.split()

def main():
    args = parse_args()

    # Handle language
    if args.lang:
        i18n.set_lang(args.lang)

    # First-run wizard or explicit --config / --setup
    if is_first_run() or args.setup:
        cfg = interactive_setup(args.lang)
        if args.setup and not args.command:
            sys.exit(0)
    else:
        cfg = load_config()

    # Engine selection
    engine_name = args.engine or cfg.get("engine", "whisper-small")
    engine = get_engine(engine_name, language=cfg.get("language", "ru"))

    # Determine command to wrap
    if args.command:
        target_command = args.command
    else:
        target_command = choose_agent_interactively()

    # Check if target binary exists in PATH
    executable = target_command[0]
    if not shutil.which(executable):
        print(f"\x1b[33m{i18n.get('agent_not_found', cmd=executable)}\x1b[0m")

    # Banner
    print("==========================================================")
    print(f"  {i18n.get('title')}")
    print(f"  {i18n.get('engine_label', engine=engine.name)}")
    print(f"  Target: {' '.join(target_command)}")
    print("==========================================================\n")

    wrapper = PtyWrapper(command=target_command, engine=engine)
    exit_code = wrapper.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
