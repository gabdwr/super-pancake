#!/bin/bash
################################################################################
# Super Pancake Bot - Oracle Linux LITE Deployment Script
# For low-memory VMs (1GB RAM) - Skips system updates
#
# Usage: bash deploy_oracle_lite.sh
################################################################################

set -e  # Exit on error

echo "🥞 Super Pancake Bot - Oracle Linux LITE Deployment"
echo "===================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$HOME/super-pancake"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

################################################################################
# Step 1: Install dependencies (NO SYSTEM UPDATE)
################################################################################
echo -e "${YELLOW}Step 1: Installing Python 3.11...${NC}"
echo "⚠️  Skipping system update to avoid OOM (Out of Memory) issues"
echo ""

# Install only what we need
sudo dnf install -y python3.11 python3.11-pip python3.11-devel git || {
    echo -e "${RED}❌ Failed to install Python 3.11${NC}"
    echo "Trying with Python 3.9 instead..."
    sudo dnf install -y python39 python39-pip python39-devel git
    PYTHON_CMD="python3.9"
}

# Set Python command (3.11 or 3.9)
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
else
    echo -e "${RED}❌ No suitable Python version found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Using $($PYTHON_CMD --version)${NC}"
echo ""

################################################################################
# Step 2: Setup project directory
################################################################################
echo -e "${YELLOW}Step 2: Setting up project directory...${NC}"

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found at $PROJECT_DIR${NC}"
    echo "Please upload your files first:"
    echo ""
    echo "  From your local machine:"
    echo "  scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/"
    echo ""
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ Project directory found${NC}"
echo ""

################################################################################
# Step 3: Create virtual environment
################################################################################
echo -e "${YELLOW}Step 3: Creating Python virtual environment...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf "$VENV_DIR"
fi

$PYTHON_CMD -m venv "$VENV_DIR"
echo -e "${GREEN}✅ Virtual environment created${NC}"
echo ""

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip (quietly)
echo "Upgrading pip..."
pip install --upgrade pip -q

################################################################################
# Step 4: Install Python dependencies (MINIMAL)
################################################################################
echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"
echo "⚠️  Installing only essential packages to save memory"
echo ""

# Install core dependencies one by one
echo "Installing web3..."
pip install web3 -q || pip install web3

echo "Installing requests..."
pip install requests -q || pip install requests

echo "Installing pandas..."
pip install pandas -q || pip install pandas

echo "Installing numpy..."
pip install numpy -q || pip install numpy

echo "Installing python-dotenv..."
pip install python-dotenv -q || pip install python-dotenv

echo ""
echo -e "${GREEN}✅ Core dependencies installed${NC}"
echo ""
echo "⚠️  Skipping optional packages (backtesting, streamlit, flask, ta-lib)"
echo "   These are not needed for token discovery."
echo ""

################################################################################
# Step 5: Configure environment variables
################################################################################
echo -e "${YELLOW}Step 5: Configuring environment variables...${NC}"

ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo ".env file already exists"
else
    echo "Creating .env file..."
    cat > "$ENV_FILE" << 'EOF'
# Super Pancake Bot - Environment Configuration

# ============================================================================
# TELEGRAM ALERTS (REQUIRED)
# ============================================================================
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# ============================================================================
# API KEYS (Optional - leave blank if not using)
# ============================================================================
MORALIS_API_KEY=
BSCSCAN_API_KEY=
ALCHEMY_BSC_RPC=https://bsc-dataseed.binance.org/

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
PAPER_TRADING=True
PAPER_TRADING_BALANCE=1000
MAX_POSITION_SIZE=50

# ============================================================================
# TOKEN FILTER CRITERIA
# ============================================================================
MIN_TOKEN_AGE_DAYS=7
MAX_TOKEN_AGE_DAYS=30
MIN_MARKET_CAP_USD=500000
MAX_MARKET_CAP_USD=5000000
MIN_LIQUIDITY_USD=10000
MIN_GOPLUS_SCORE=70

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
DEBUG_MODE=False
EOF

    echo -e "${GREEN}✅ .env file created${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file NOW${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You MUST add your Telegram credentials:"
echo "  • TELEGRAM_BOT_TOKEN"
echo "  • TELEGRAM_CHAT_ID"
echo ""
read -p "Press Enter to edit .env file now..."
nano "$ENV_FILE"

echo ""

################################################################################
# Step 6: Create log directory
################################################################################
echo -e "${YELLOW}Step 6: Creating log directory...${NC}"

mkdir -p "$LOG_DIR"
echo -e "${GREEN}✅ Log directory created${NC}"
echo ""

################################################################################
# Step 7: Verify installation
################################################################################
echo -e "${YELLOW}Step 7: Verifying installation...${NC}"

echo "Checking Python packages..."
pip list | grep -E "web3|requests|pandas|numpy|python-dotenv"

echo ""
echo "Checking .env configuration..."
if grep -q "^TELEGRAM_BOT_TOKEN=.\+" "$ENV_FILE" && grep -q "^TELEGRAM_CHAT_ID=.\+" "$ENV_FILE"; then
    echo -e "${GREEN}✅ Telegram credentials configured${NC}"
else
    echo -e "${YELLOW}⚠️  Telegram credentials NOT set - alerts will not work${NC}"
fi

echo ""

################################################################################
# Deployment Complete
################################################################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ LITE Deployment Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Python: $($PYTHON_CMD --version)"
echo "Virtual env: $VENV_DIR"
echo "Logs: $LOG_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test the bot manually:"
echo "   cd ~/super-pancake"
echo "   source venv/bin/activate"
echo "   python test_discovery_and_liquidity.py"
echo ""
echo "2. If test works, cron is already configured!"
echo "   Your bot will run every hour automatically."
echo ""
echo "3. Check logs:"
echo "   tail -f ~/super-pancake/logs/discovery_*.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🥞 Happy token hunting!"
echo ""
