#!/bin/bash
################################################################################
# Super Pancake Bot - Cron Setup Script
#
# This script configures crontab to run token discovery automatically
#
# Schedule options:
#   - Every 6 hours: 0 */6 * * *  (00:00, 06:00, 12:00, 18:00 UTC)
#   - Every hour:    0 * * * *
#   - Every 4 hours: 0 */4 * * *
#
# Usage: bash setup_cron.sh
################################################################################

set -e

echo "🥞 Super Pancake Bot - Cron Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$HOME/super-pancake"
WRAPPER_SCRIPT="$PROJECT_DIR/scripts/run_discovery_cron.sh"
CRON_LOG="$PROJECT_DIR/logs/cron.log"

# Check if wrapper script exists
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo "❌ ERROR: Wrapper script not found at $WRAPPER_SCRIPT"
    echo "Please run ./scripts/deploy_oracle.sh first"
    exit 1
fi

# Make wrapper script executable
chmod +x "$WRAPPER_SCRIPT"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo "Choose execution schedule:"
echo ""
echo "  1) Every 6 hours (recommended) - 00:00, 06:00, 12:00, 18:00 UTC"
echo "  2) Every 4 hours - 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC"
echo "  3) Every hour"
echo "  4) Every 12 hours - 00:00, 12:00 UTC"
echo "  5) Custom schedule"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="every 6 hours"
        ;;
    2)
        CRON_SCHEDULE="0 */4 * * *"
        DESCRIPTION="every 4 hours"
        ;;
    3)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="every hour"
        ;;
    4)
        CRON_SCHEDULE="0 */12 * * *"
        DESCRIPTION="every 12 hours"
        ;;
    5)
        echo ""
        echo "Enter cron schedule in standard format (minute hour day month weekday):"
        echo "Examples:"
        echo "  0 */6 * * *   - Every 6 hours"
        echo "  30 */2 * * *  - Every 2 hours at :30 minutes"
        echo "  0 8,20 * * *  - At 8:00 AM and 8:00 PM"
        echo ""
        read -p "Enter schedule: " CRON_SCHEDULE
        DESCRIPTION="custom schedule: $CRON_SCHEDULE"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Build cron job entry
CRON_JOB="$CRON_SCHEDULE $WRAPPER_SCRIPT >> $CRON_LOG 2>&1"

echo ""
echo -e "${YELLOW}Configuring cron job...${NC}"
echo "Schedule: $DESCRIPTION"
echo "Command: $WRAPPER_SCRIPT"
echo ""

# Backup existing crontab
echo "Backing up existing crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$WRAPPER_SCRIPT"; then
    echo "⚠️  Cron job already exists for this script"
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old entry
        crontab -l 2>/dev/null | grep -v "$WRAPPER_SCRIPT" | crontab -
        echo "Old cron job removed"
    else
        echo "Keeping existing cron job"
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo ""; echo "# Super Pancake Token Discovery Bot"; echo "$CRON_JOB") | crontab -

echo ""
echo -e "${GREEN}✅ Cron job configured successfully!${NC}"
echo ""
echo "Schedule: $DESCRIPTION"
echo "Cron expression: $CRON_SCHEDULE"
echo ""

# Display current crontab
echo "Current crontab:"
echo "─────────────────────────────────────────────────"
crontab -l
echo "─────────────────────────────────────────────────"
echo ""

# Test the wrapper script
echo -e "${YELLOW}Testing wrapper script...${NC}"
read -p "Do you want to run a test now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running test..."
    bash "$WRAPPER_SCRIPT"
    echo ""
    echo "Test complete! Check the output above for any errors."
    echo ""
fi

# Show next execution times
echo "Next scheduled executions:"
echo "─────────────────────────────────────────────────"

# This is a simple calculation, not perfect but gives an idea
current_hour=$(date +%H)
current_minute=$(date +%M)

case $choice in
    1)  # Every 6 hours
        next_times=(0 6 12 18)
        ;;
    2)  # Every 4 hours
        next_times=(0 4 8 12 16 20)
        ;;
    3)  # Every hour
        next_times=($(seq 0 23))
        ;;
    4)  # Every 12 hours
        next_times=(0 12)
        ;;
    *)
        next_times=()
        ;;
esac

if [ ${#next_times[@]} -gt 0 ]; then
    count=0
    for hour in "${next_times[@]}"; do
        if [ $hour -gt $current_hour ] || ([ $hour -eq $current_hour ] && [ $current_minute -lt 0 ]); then
            echo "  Today at $(printf '%02d:00' $hour) UTC"
            count=$((count + 1))
            if [ $count -ge 3 ]; then
                break
            fi
        fi
    done

    if [ $count -lt 3 ]; then
        for hour in "${next_times[@]}"; do
            if [ $count -lt 3 ]; then
                echo "  Tomorrow at $(printf '%02d:00' $hour) UTC"
                count=$((count + 1))
            fi
        done
    fi
fi

echo "─────────────────────────────────────────────────"
echo ""

echo "Useful commands:"
echo "  • View crontab: crontab -l"
echo "  • Edit crontab: crontab -e"
echo "  • View cron log: tail -f $CRON_LOG"
echo "  • View discovery logs: tail -f $PROJECT_DIR/logs/discovery_*.log"
echo "  • Test manually: bash $WRAPPER_SCRIPT"
echo "  • Remove cron job: crontab -e (then delete the line)"
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Your bot will now run $DESCRIPTION and send Telegram alerts."
echo "Make sure your Telegram credentials are configured in .env"
echo ""
echo "🥞 Happy automated token hunting!"
