#!/bin/bash
################################################################################
# Super Pancake Bot - Cron Wrapper Script
#
# This script wraps the token discovery script for execution via cron
# Features:
#   - Activates virtual environment
#   - Logs output with timestamps
#   - Sends error alerts via Telegram
#   - Handles cleanup
#
# Usage: ./scripts/run_discovery_cron.sh
################################################################################

# Exit on error
set -e

# Configuration
PROJECT_DIR="$HOME/super-pancake"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
SCRIPT_PATH="$PROJECT_DIR/test_discovery_and_liquidity.py"

# Create timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/discovery_$TIMESTAMP.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

################################################################################
# Logging function
################################################################################
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

################################################################################
# Error handler
################################################################################
error_handler() {
    local exit_code=$?
    log "❌ ERROR: Script failed with exit code $exit_code"

    # Try to send Telegram alert about the error
    if [ -f "$VENV_DIR/bin/python" ]; then
        "$VENV_DIR/bin/python" -c "
from src.utils.telegram_alerts import send_error
send_error('Token discovery script failed with exit code $exit_code', 'Cron Job')
" 2>/dev/null || log "Failed to send Telegram error alert"
    fi

    exit $exit_code
}

# Set error handler
trap error_handler ERR

################################################################################
# Main execution
################################################################################

log "🥞 Super Pancake Bot - Starting Token Discovery"
log "================================================"

# Change to project directory
cd "$PROJECT_DIR" || {
    log "❌ ERROR: Could not change to project directory: $PROJECT_DIR"
    exit 1
}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    log "❌ ERROR: Virtual environment not found at $VENV_DIR"
    log "Please run ./scripts/deploy_oracle.sh first"
    exit 1
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || {
    log "❌ ERROR: Failed to activate virtual environment"
    exit 1
}

# Verify Python
PYTHON_VERSION=$("$VENV_DIR/bin/python" --version 2>&1)
log "Python version: $PYTHON_VERSION"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    log "❌ ERROR: Discovery script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log "⚠️  WARNING: .env file not found - Telegram alerts may not work"
fi

# Run the discovery script
log "Running token discovery script..."
log "Output will be saved to: $LOG_FILE"
log ""

# Execute the script and capture output
if "$VENV_DIR/bin/python" "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1; then
    log ""
    log "✅ Token discovery completed successfully"
    log "================================================"
else
    log ""
    log "❌ Token discovery failed"
    log "================================================"
    exit 1
fi

# Deactivate virtual environment
deactivate 2>/dev/null || true

# Log cleanup
log "Cleaning up old log files (keeping last 30 days)..."
find "$LOG_DIR" -name "discovery_*.log" -type f -mtime +30 -delete 2>/dev/null || true
log "Cleanup complete"

# Final status
log "Script finished at $(date +'%Y-%m-%d %H:%M:%S')"

exit 0
