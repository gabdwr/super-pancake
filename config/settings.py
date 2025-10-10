"""
Super Pancake - Configuration Settings
Load environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API Keys
# =============================================================================

# GoPlus doesn't need an API key - free tier works without authentication
MORALIS_API_KEY = os.getenv('MORALIS_API_KEY')
ALCHEMY_BSC_RPC = os.getenv('ALCHEMY_BSC_RPC', 'https://bsc-dataseed.binance.org/')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')  # Optional

# Telegram (optional for alerts)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# =============================================================================
# Blockchain Configuration
# =============================================================================

BSC_CHAIN_ID = 56
BSC_EXPLORER = 'https://bscscan.com'
BSC_RPC_URL = ALCHEMY_BSC_RPC

# =============================================================================
# Trading Parameters
# =============================================================================

# Paper Trading (NEVER set to False until Phase 8!)
PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
STARTING_BALANCE = float(os.getenv('PAPER_TRADING_BALANCE', 1000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 50))
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', 10))

# =============================================================================
# Risk Management
# =============================================================================

STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', -50))
TAKE_PROFIT_T1_PERCENT = float(os.getenv('TAKE_PROFIT_T1_PERCENT', 100))
TAKE_PROFIT_T2_PERCENT = float(os.getenv('TAKE_PROFIT_T2_PERCENT', 300))

# =============================================================================
# Token Filter Criteria
# =============================================================================

MIN_TOKEN_AGE_DAYS = int(os.getenv('MIN_TOKEN_AGE_DAYS', 7))
MAX_TOKEN_AGE_DAYS = int(os.getenv('MAX_TOKEN_AGE_DAYS', 30))
MIN_MARKET_CAP_USD = int(os.getenv('MIN_MARKET_CAP_USD', 500000))
MAX_MARKET_CAP_USD = int(os.getenv('MAX_MARKET_CAP_USD', 5000000))
MIN_LIQUIDITY_USD = int(os.getenv('MIN_LIQUIDITY_USD', 50000))
MIN_GOPLUS_SCORE = int(os.getenv('MIN_GOPLUS_SCORE', 70))
MAX_GINI_COEFFICIENT = float(os.getenv('MAX_GINI_COEFFICIENT', 0.7))

# =============================================================================
# Database Configuration
# =============================================================================

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/superpancake')

# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'True').lower() == 'true'

# =============================================================================
# Development Mode
# =============================================================================

DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'


# =============================================================================
# Validation
# =============================================================================

def validate_settings():
    """Validate that required settings are present"""
    errors = []

    if not MORALIS_API_KEY:
        errors.append("MORALIS_API_KEY is not set in .env file")

    if not ALCHEMY_BSC_RPC:
        errors.append("ALCHEMY_BSC_RPC is not set in .env file")

    if PAPER_TRADING is False:
        errors.append("⚠️  WARNING: PAPER_TRADING is False! Only use real capital in Phase 8+")

    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return False

    print("✅ Configuration validated successfully")
    return True


if __name__ == "__main__":
    # Test configuration
    print("Super Pancake - Configuration Test")
    print("=" * 60)
    print(f"Paper Trading: {PAPER_TRADING}")
    print(f"Starting Balance: ${STARTING_BALANCE}")
    print(f"Max Position Size: ${MAX_POSITION_SIZE}")
    print(f"Token Age Filter: {MIN_TOKEN_AGE_DAYS}-{MAX_TOKEN_AGE_DAYS} days")
    print(f"Market Cap Filter: ${MIN_MARKET_CAP_USD:,} - ${MAX_MARKET_CAP_USD:,}")
    print(f"BSC Chain ID: {BSC_CHAIN_ID}")
    print("=" * 60)
    validate_settings()
