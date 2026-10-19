#!/bin/bash
# AgroNex-Pi Robot Launcher
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="/usr/bin/python3"
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
elif [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
fi

echo "[AgroNex-Pi] Launching main.py from: $SCRIPT_DIR using $PYTHON_BIN"
exec "$PYTHON_BIN" "$SCRIPT_DIR/main.py"
