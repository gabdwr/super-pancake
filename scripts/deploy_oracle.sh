#!/bin/bash
################################################################################
# Super Pancake Bot - Oracle Linux VM Deployment Script
#
# This script automates deployment on Oracle Linux VM
# Usage: bash deploy_oracle.sh
################################################################################

set -e  # Exit on error

echo "🥞 Super Pancake Bot - Oracle Linux Deployment"
echo "=============================================="
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
# Step 1: Update system and install dependencies
################################################################################
echo -e "${YELLOW}Step 1: Installing system dependencies...${NC}"

# Update package manager
sudo dnf update -y

# Install Python 3.11 (Oracle Linux 8/9)
echo "Installing Python 3.11..."
sudo dnf install -y python3.11 python3.11-pip python3.11-devel

# Install git
echo "Installing git..."
sudo dnf install -y git

# Install development tools (needed for some Python packages)
echo "Installing development tools..."
sudo dnf groupinstall -y "Development Tools"

echo -e "${GREEN}✅ System dependencies installed${NC}"
echo ""

################################################################################
# Step 2: Clone or verify project directory
################################################################################
echo -e "${YELLOW}Step 2: Setting up project directory...${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo "Project directory already exists at $PROJECT_DIR"
    read -p "Do you want to pull latest changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_DIR"
        git pull
    fi
else
    echo "Project directory not found."
    echo ""
    echo "Choose deployment method:"
    echo "  1) Clone from GitHub (if you have a repo)"
    echo "  2) I'll upload files manually via SCP"
    echo ""
    read -p "Enter choice (1 or 2): " choice

    if [ "$choice" = "1" ]; then
        read -p "Enter your GitHub repository URL: " repo_url
        git clone "$repo_url" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    else
        echo ""
        echo "Please upload your files using SCP from your local machine:"
        echo ""
        echo "  scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/"
        echo ""
        read -p "Press Enter after you've uploaded the files..."

        if [ ! -d "$PROJECT_DIR" ]; then
            echo -e "${RED}❌ Project directory not found. Please upload files and try again.${NC}"
            exit 1
        fi
        cd "$PROJECT_DIR"
    fi
fi

echo -e "${GREEN}✅ Project directory ready${NC}"
echo ""

################################################################################
# Step 3: Create virtual environment
################################################################################
echo -e "${YELLOW}Step 3: Creating Python virtual environment...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists"
else
    python3.11 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

echo ""

################################################################################
# Step 4: Install Python dependencies
################################################################################
echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    # Install core dependencies (skip optional ones that might fail)
    pip install web3 requests pandas numpy python-dotenv

    echo ""
    echo "Core dependencies installed. Attempting full requirements.txt..."

    # Try full install, but don't fail if some packages don't install
    pip install -r requirements.txt || echo "Some optional packages failed to install (this is OK)"

    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo ""

################################################################################
# Step 5: Configure environment variables
################################################################################
echo -e "${YELLOW}Step 5: Configuring environment variables...${NC}"

ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo ".env file already exists"
    read -p "Do you want to edit it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano "$ENV_FILE"
    fi
else
    echo "Creating .env file..."
    cat > "$ENV_FILE" << 'EOF'
# Super Pancake Bot - Environment Configuration

# Telegram Alerts (REQUIRED for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# API Keys (optional for enhanced features)
MORALIS_API_KEY=your_moralis_key_here
ALCHEMY_BSC_RPC=https://bsc-dataseed.binance.org/
BSCSCAN_API_KEY=your_bscscan_key_here

# Trading Parameters
PAPER_TRADING=True
PAPER_TRADING_BALANCE=1000
MAX_POSITION_SIZE=50

# Token Filter Criteria
MIN_TOKEN_AGE_DAYS=7
MAX_TOKEN_AGE_DAYS=30
MIN_MARKET_CAP_USD=500000
MAX_MARKET_CAP_USD=5000000
MIN_LIQUIDITY_USD=10000
MIN_GOPLUS_SCORE=70

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=False
EOF

    echo ""
    echo "✅ .env file created with template"
    echo ""
    echo "⚠️  IMPORTANT: You MUST edit .env and add your API keys:"
    echo "   - TELEGRAM_BOT_TOKEN (required for alerts)"
    echo "   - TELEGRAM_CHAT_ID (required for alerts)"
    echo ""
    read -p "Press Enter to edit .env file now..."
    nano "$ENV_FILE"
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

################################################################################
# Step 6: Create log directory
################################################################################
echo -e "${YELLOW}Step 6: Creating log directory...${NC}"

mkdir -p "$LOG_DIR"
echo -e "${GREEN}✅ Log directory created at $LOG_DIR${NC}"
echo ""

################################################################################
# Step 7: Test the bot
################################################################################
echo -e "${YELLOW}Step 7: Testing bot...${NC}"

read -p "Do you want to run a test now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running test discovery..."
    python test_discovery_and_liquidity.py
    echo ""
fi

################################################################################
# Deployment Complete
################################################################################
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Run './scripts/setup_cron.sh' to configure automated execution"
echo "  2. Check logs in: $LOG_DIR"
echo "  3. Monitor via Telegram alerts"
echo ""
echo "Useful commands:"
echo "  • Activate venv: source $VENV_DIR/bin/activate"
echo "  • Run manually: cd $PROJECT_DIR && python test_discovery_and_liquidity.py"
echo "  • View logs: tail -f $LOG_DIR/discovery_*.log"
echo "  • Edit crontab: crontab -e"
echo ""
echo "🥞 Happy token hunting!"
