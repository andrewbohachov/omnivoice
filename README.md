# OmniVoice

**[English](README.md)** | [Русский](README_RU.md)

Voice Prompting & Speech Dictation for Terminal AI Agents (Antigravity CLI, Claude Code, Codex, Aider).  
**Zero API keys required. Push-to-Talk via Caps Lock. Tuned for developer and coding terminology.**

OmniVoice wraps your favorite console AI coding assistant in a transparent terminal wrapper, allowing you to speak long, complex engineering prompts naturally instead of typing hundreds of characters by hand.

---

## Key Features

* **Tailored for AI Coding Assistants:** Designed specifically for `agy` (Antigravity CLI), `claude` (Claude Code), `codex`, `aider`, and system shells.
* **Effortless Caps Lock Toggle:** Press `Caps Lock` once to start speaking; press `Caps Lock` again to stop. The transcribed prompt is instantly typed into the agent's input line.
* **Developer Vocabulary Tuning:** Accurately recognizes technical English keywords (`API`, `FastAPI`, `Redis`, `Git`, `Docker`, `pull request`, `pytest`) even when spoken conversationally.
* **Interactive First-Run Wizard:** Choose your preferred speech-to-text engine with an interactive terminal arrow-key menu:
  * **Whisper Small (Recommended):** ~480 MB, 100% offline, balanced speed (~2 sec) and high technical accuracy.
  * **Google Speech:** 0 MB download, fast cloud API, zero RAM usage, no API keys needed.
  * **Whisper Turbo (Large-v3):** ~1.6 GB, maximum accuracy for high-end workstations.
* **Interactive Agent Selector:** Run `omnivoice` without arguments to choose an installed AI agent from a menu, or launch directly via `omnivoice agy` / `omnivoice claude`.
* **Clean Linux Architecture:** Works seamlessly on both Wayland and X11 via direct evdev keyboard events.

---

## Installation

### Method 1: Single-Command Shell Installer (Recommended)

Automatically installs required system packages (`ffmpeg`, `libportaudio2`), configures input permissions, downloads the default Whisper Small model, and registers the global `omnivoice` command:

```bash
curl -fsSL https://raw.githubusercontent.com/andrewbohachov/omnivoice/main/install.sh | bash
```

### Method 2: Debian / Ubuntu Package (.deb)

Download the pre-compiled `.deb` package and install via APT:

```bash
sudo apt install ./omnivoice_0.1.0_all.deb
```

### Method 3: Manual Clone & pip

```bash
# 1. Install prerequisites (Debian / Ubuntu / Mint)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg libportaudio2

# 2. Clone repository and install package
git clone https://github.com/andrewbohachov/omnivoice.git
cd omnivoice
pip install -e .

# 3. Global symlink
sudo ln -sf $(which omnivoice) /usr/local/bin/omnivoice
```

---

## Quick Usage

### 1. Launch with Your Preferred Agent

Run directly with any command:
```bash
# Launch with Antigravity CLI
omnivoice agy

# Launch with Claude Code
omnivoice claude

# Launch with Codex CLI
omnivoice codex

# Launch with Bash
omnivoice bash
```

Or run `omnivoice` without arguments to open the interactive agent selector:
```bash
omnivoice
```

### 2. Dictate Prompts with Caps Lock

1. While inside the agent's chat prompt, press **`Caps Lock`** once.
2. The terminal displays `[● REC] Listening...`. Speak your prompt into your microphone:
   > *"Refactor the API endpoints in server.py, add Redis caching, and run the test suite."*
3. Press **`Caps Lock`** a second time to stop recording.
4. The transcribed text is automatically typed into the prompt line.
5. Review, edit if needed, and press **`Enter`** to send!

---

## Command-Line Arguments

```
omnivoice [OPTIONS] [COMMAND...]

Arguments:
  command              AI agent command to wrap (default: interactive menu)

Options:
  --engine {small,google,turbo}  Override speech recognition engine
  --lang {en,ru}                 Set interface language (default: en)
  --setup, --config              Re-run interactive engine selection wizard
  -h, --help                     Show this help message
```

### Examples:
```bash
# Launch Claude Code with default engine
omnivoice claude

# Launch Antigravity CLI with Google Speech engine (0 MB RAM)
omnivoice --engine google agy

# Change default engine in interactive wizard
omnivoice --config
```

---

## License

MIT License. Free and open source.
