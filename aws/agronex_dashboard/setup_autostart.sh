#!/bin/bash
# ============================================================
# AgroNex-Pi Auto-Start Setup Script
# Run this ONCE on the Raspberry Pi as: sudo bash setup_autostart.sh
# ============================================================
set -e

# 1. Detect Real User (handles 'nikhil', 'pi', or whoever runs sudo)
ACTUAL_USER="${SUDO_USER:-$(logname 2>/dev/null || whoami)}"
ACTUAL_HOME="$(getent passwd "$ACTUAL_USER" | cut -d: -f6)"
if [ -z "$ACTUAL_HOME" ]; then
    ACTUAL_HOME="/home/$ACTUAL_USER"
fi

# 2. Locate Project Directory and main.py
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$PROJECT_DIR/main.py" ]; then
    if [ -f "$ACTUAL_HOME/Major project/main.py" ]; then
        PROJECT_DIR="$ACTUAL_HOME/Major project"
    elif [ -f "$ACTUAL_HOME/major_project/main.py" ]; then
        PROJECT_DIR="$ACTUAL_HOME/major_project"
    else
        echo "[ERROR] Could not find main.py in '$PROJECT_DIR' or '$ACTUAL_HOME/Major project'."
        exit 1
    fi
fi

# 3. Locate Python executable (checks venv first, then system python3)
PYTHON_BIN="/usr/bin/python3"
if [ -f "$PROJECT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$PROJECT_DIR/venv/bin/python3"
elif [ -f "$PROJECT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
fi

# Locate sleep binary
SLEEP_BIN="$(command -v sleep 2>/dev/null || echo '/bin/sleep')"

INSTALL_PATH="/etc/systemd/system/agronex.service"
RUNNER_SCRIPT="$PROJECT_DIR/start_agronex.sh"

echo "================================================="
echo " AgroNex-Pi Auto-Start Installer"
echo " Detected User:     $ACTUAL_USER"
echo " Project Directory: $PROJECT_DIR"
echo " Python Path:       $PYTHON_BIN"
echo " Sleep Utility:     $SLEEP_BIN"
echo " Runner Script:     $RUNNER_SCRIPT"
echo " Target Service:    $INSTALL_PATH"
echo "================================================="

# 4. Stop existing service or running processes
echo "[1/6] Stopping any existing agronex service..."
systemctl stop agronex.service 2>/dev/null || true

# 5. Create launcher runner script
echo "[2/6] Preparing launcher script at $RUNNER_SCRIPT ..."
cat <<EOF > "$RUNNER_SCRIPT"
#!/bin/bash
cd "$PROJECT_DIR"
exec "$PYTHON_BIN" "$PROJECT_DIR/main.py"
EOF
chmod +x "$RUNNER_SCRIPT"
chown "$ACTUAL_USER:$ACTUAL_USER" "$RUNNER_SCRIPT" 2>/dev/null || true

# 6. Generate tailored systemd unit file
# Note: systemd requires WorkingDirectory to be unquoted absolute path
echo "[3/6] Writing /etc/systemd/system/agronex.service ..."
cat <<EOF > "$INSTALL_PATH"
[Unit]
Description=AgroNex-Pi Autonomous Farm Robot Controller
Documentation=https://github.com/agronex-pi
After=network-online.target multi-user.target
Wants=network-online.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR

# Launch immediately without delay
ExecStart=/bin/bash "$RUNNER_SCRIPT"

# Auto-restart on crash
Restart=on-failure
RestartSec=10s

# Journal logging
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$INSTALL_PATH"

# 7. Reload systemd daemon
echo "[4/6] Reloading systemd daemon..."
systemctl daemon-reload

# 8. Enable service (auto-start on boot)
echo "[5/6] Enabling agronex.service for auto-start on boot..."
systemctl enable agronex.service

# 9. Start service with live status capture
echo "[6/6] Starting agronex.service now (waiting 20s for initial start)..."
if ! systemctl start agronex.service; then
    echo ""
    echo "================================================="
    echo " [!] SERVICE FAILED TO START. ERROR DETAILS:"
    echo "================================================="
    systemctl status agronex.service --no-pager || true
    echo "-------------------------------------------------"
    echo " Recent journal logs:"
    journalctl -u agronex.service -n 25 --no-pager || true
    echo "================================================="
    exit 1
fi

echo ""
echo "================================================="
echo " SUCCESS! AgroNex-Pi service is active."
echo " It will now automatically launch main.py 20s"
echo " after every time the Raspberry Pi powers on."
echo ""
echo " Useful commands:"
echo "  sudo systemctl status agronex   -> check status"
echo "  sudo journalctl -u agronex -f   -> live logs"
echo "  sudo systemctl stop agronex     -> stop robot"
echo "  sudo systemctl restart agronex  -> restart robot"
echo "================================================="
