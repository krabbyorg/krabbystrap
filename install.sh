#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
APP_NAME="Krabbystrap"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/krabbystrap.desktop"

# ── colours ────────────────────────────────────────────────────────────────
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'
ok()   { echo -e "  ${G}✓${N}  $*"; }
step() { echo -e "  ${Y}→${N}  $*"; }
err()  { echo -e "  ${R}✗${N}  $*"; }

echo ""
echo -e "  ${Y}Installing ${APP_NAME}…${N}"
echo ""

# ── dependency checks ──────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    err "python3 not found — install it first"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if python3 -c 'import sys; exit(0 if sys.version_info >= (3,11) else 1)'; then
    ok "Python $PY_VER"
else
    err "Python 3.11+ required (found $PY_VER)"
    exit 1
fi

if ! command -v flatpak &>/dev/null; then
    err "flatpak not found — Sober won't work without it"
    exit 1
else
    ok "flatpak"
fi

if ! flatpak list --app 2>/dev/null | grep -q "org.vinegarhq.Sober"; then
    echo -e "  ${Y}!${N}  Sober (org.vinegarhq.Sober) not installed — install it from https://sober.vinegarhq.org/"
else
    ok "Sober"
fi

# ── virtual environment ────────────────────────────────────────────────────
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    step "Creating virtual environment…"
    python3 -m venv "$SCRIPT_DIR/.venv"
    ok "Virtual environment created"
else
    ok "Virtual environment exists"
fi

step "Installing Python dependencies…"
"$SCRIPT_DIR/.venv/bin/pip" install -q --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
ok "Dependencies installed"

# ── permissions ────────────────────────────────────────────────────────────
chmod +x "$SCRIPT_DIR/krabbystrap.sh"

# ── desktop entry ──────────────────────────────────────────────────────────
step "Creating desktop entry…"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=Roblox launcher for Linux via Sober
Exec=$SCRIPT_DIR/krabbystrap.sh
Icon=$SCRIPT_DIR/assets/krabby.png
Type=Application
Categories=Game;
Terminal=false
StartupWMClass=Krabbystrap
Actions=Settings;

[Desktop Action Settings]
Name=Open Settings
Exec=$SCRIPT_DIR/krabbystrap.sh --settings
EOF

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi
ok "Desktop entry created"

# ── done ───────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${G}All done!${N}"
echo ""
echo "  Launch:    $SCRIPT_DIR/krabbystrap.sh"
echo "  Settings:  $SCRIPT_DIR/krabbystrap.sh --settings"
echo "  App menu:  search for '$APP_NAME'"
echo ""
