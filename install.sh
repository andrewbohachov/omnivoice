#!/usr/bin/env bash
set -e

# ==============================================================================
# OmniVoice One-Line Installer
# Supports local execution and remote curl execution:
#   curl -fsSL https://raw.githubusercontent.com/andrewbohachov/omnivoice/main/install.sh | bash
# ==============================================================================

REPO_URL="https://github.com/andrewbohachov/omnivoice.git"
INSTALL_DIR="${HOME}/.local/share/omnivoice"
BIN_DIR="${HOME}/.local/bin"

echo "=========================================================="
echo "               OMNIVOICE INSTALLER                        "
echo "=========================================================="

mkdir -p "$BIN_DIR"
mkdir -p "${HOME}/.local/share"

# [1/5] Install system packages (ffmpeg, portaudio, python3-venv)
echo "[1/5] Checking system dependencies..."
if command -v apt-get &>/dev/null; then
    MISSING_PKGS=""
    for pkg in python3 python3-pip python3-venv ffmpeg libportaudio2; do
        if ! dpkg -s "$pkg" &>/dev/null; then
            MISSING_PKGS="$MISSING_PKGS $pkg"
        fi
    done
    if [ -n "$MISSING_PKGS" ]; then
        echo "[*] Installing missing system packages:$MISSING_PKGS"
        sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y $MISSING_PKGS
    else
        echo "[*] System packages already satisfied."
    fi
elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed --noconfirm python python-pip ffmpeg portaudio
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3 python3-pip ffmpeg portaudio
fi

# [2/5] Setup udev rule for Caps Lock keyboard events
echo "[2/5] Configuring keyboard access permissions..."
if command -v sudo &>/dev/null; then
    if [ ! -f /etc/udev/rules.d/99-omnivoice-input.rules ]; then
        echo 'KERNEL=="event*", MODE="0666"' | sudo tee /etc/udev/rules.d/99-omnivoice-input.rules >/dev/null
        sudo udevadm control --reload-rules 2>/dev/null || true
        sudo udevadm trigger 2>/dev/null || true
    fi
fi

# [3/5] Setup OmniVoice source files
echo "[3/5] Setting up OmniVoice source files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

if [ -f "$SCRIPT_DIR/pyproject.toml" ] && [ -d "$SCRIPT_DIR/omnivoice" ]; then
    echo "[*] Installing from local repository ($SCRIPT_DIR)..."
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR"/.* "$INSTALL_DIR/" 2>/dev/null || true
else
    echo "[*] Cloning latest OmniVoice repository from GitHub..."
    if [ -d "$INSTALL_DIR/.git" ]; then
        git -C "$INSTALL_DIR" pull --quiet
    else
        rm -rf "$INSTALL_DIR"
        git clone --quiet "$REPO_URL" "$INSTALL_DIR"
    fi
fi

# [4/5] Create virtualenv and install Python dependencies
echo "[4/5] Preparing isolated virtual environment..."
VENV_DIR="$INSTALL_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$INSTALL_DIR"

# Pre-cache default Whisper Small model
echo "[*] Pre-caching default Whisper Small model (~480 MB)..."
"$VENV_DIR/bin/python" -c "
try:
    from faster_whisper import WhisperModel
    WhisperModel('small', device='cpu', compute_type='int8')
except Exception as e:
    pass
" || true

# Create binary launcher wrapper in ~/.local/bin
cat <<EOF > "$BIN_DIR/omnivoice"
#!/usr/bin/env bash
exec "$VENV_DIR/bin/omnivoice" "\$@"
EOF
chmod +x "$BIN_DIR/omnivoice"

# Create global symlink in /usr/local/bin if possible
if [ -w /usr/local/bin ]; then
    ln -sf "$BIN_DIR/omnivoice" /usr/local/bin/omnivoice 2>/dev/null || true
elif command -v sudo &>/dev/null; then
    sudo ln -sf "$BIN_DIR/omnivoice" /usr/local/bin/omnivoice 2>/dev/null || true
fi

# [5/5] Verify PATH
echo "[5/5] Verifying PATH..."
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    ADDED_TO=""
    if [ -f "$HOME/.bashrc" ] && ! grep -q 'HOME/\.local/bin' "$HOME/.bashrc" && ! grep -q '\$HOME/\.local/bin' "$HOME/.bashrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        ADDED_TO="~/.bashrc"
    fi
    if [ -f "$HOME/.zshrc" ] && ! grep -q 'HOME/\.local/bin' "$HOME/.zshrc" && ! grep -q '\$HOME/\.local/bin' "$HOME/.zshrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        ADDED_TO="${ADDED_TO:+$ADDED_TO, }~/.zshrc"
    fi
    if [ -n "$ADDED_TO" ]; then
        echo "[*] Added $BIN_DIR to PATH in $ADDED_TO."
    fi
fi

echo ""
echo "=========================================================="
echo "               OMNIVOICE SUCCESSFULLY INSTALLED           "
echo "=========================================================="
echo ""
echo "Run anywhere in terminal:"
echo "  omnivoice"
echo ""
echo "Or wrap specific AI agent directly:"
echo "  omnivoice agy        # Antigravity CLI"
echo "  omnivoice claude     # Claude Code"
echo "  omnivoice codex      # Codex CLI"
echo "  omnivoice bash       # System shell"
echo ""
echo "Inside any agent, press [Caps Lock] to speak and prompt!"
echo "=========================================================="
