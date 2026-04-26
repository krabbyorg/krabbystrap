#!/bin/bash
VENV_DIR="$HOME/.local/share/krabbystrap/venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" 2>/dev/null || exit 1
    "$VENV_DIR/bin/pip" install -q -r /usr/lib/krabbystrap/requirements.txt 2>/dev/null || exit 1
fi
exec "$VENV_DIR/bin/python3" /usr/lib/krabbystrap/src/launch.py "$@"
