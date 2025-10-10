"""
Super Pancake - Trading Constants
Constants that don't change based on environment
"""

# =============================================================================
# DEX Addresses (PancakeSwap V2 on BSC)
# =============================================================================

PANCAKESWAP_ROUTER_V2 = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
PANCAKESWAP_FACTORY_V2 = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'

# Common token addresses on BSC
WBNB_ADDRESS = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
USDT_ADDRESS = '0x55d398326f99059fF775485246999027B3197955'  # BSC-USD
BUSD_ADDRESS = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'  # Binance-Peg BUSD

# =============================================================================
# Token Filter Criteria (Defaults)
# =============================================================================

# Age filters (days)
MIN_TOKEN_AGE_DAYS = 7
MAX_TOKEN_AGE_DAYS = 30

# Market cap filters (USD)
MIN_MARKET_CAP_USD = 500_000      # $500K
MAX_MARKET_CAP_USD = 5_000_000    # $5M

# Liquidity filters
MIN_LIQUIDITY_USD = 50_000        # $50K minimum liquidity
MIN_LIQUIDITY_LOCK_DAYS = 180     # 6 months minimum lock

# =============================================================================
# Security Thresholds
# =============================================================================

# GoPlus security score (0-100)
MIN_GOPLUS_SCORE = 70

# Holder distribution (Gini coefficient 0-1)
# 0 = perfectly equal, 1 = one person owns everything
MAX_GINI_COEFFICIENT = 0.7

# Volume/Liquidity ratio (wash trading detection)
MIN_VOLUME_LIQUIDITY_RATIO = 0.5
MAX_VOLUME_LIQUIDITY_RATIO = 3.0

# Minimum holder count
MIN_HOLDER_COUNT = 100

# Maximum single wallet ownership (%)
MAX_SINGLE_WALLET_PERCENT = 20

# =============================================================================
# Risk Management
# =============================================================================

# Position sizing
MAX_POSITION_PERCENT = 2    # Max 2% of portfolio per trade
MAX_TOTAL_EXPOSURE = 20     # Max 20% total exposure (10 positions)

# Stop loss / Take profit
STOP_LOSS_PERCENT = -50           # Cut at -50%
TAKE_PROFIT_T1_PERCENT = 100      # First TP at +100% (2x)
TAKE_PROFIT_T1_SIZE = 0.5         # Sell 50% at T1
TAKE_PROFIT_T2_PERCENT = 300      # Second TP at +300% (4x)
TAKE_PROFIT_T2_SIZE = 0.25        # Sell 25% at T2
TRAILING_STOP_PERCENT = 30        # Trail remaining 25% with 30% stop

# =============================================================================
# Trading Rules
# =============================================================================

# Max trades per day (circuit breaker)
MAX_TRADES_PER_DAY = 5

# Pause trading after X consecutive losses
MAX_CONSECUTIVE_LOSSES = 3

# Max daily drawdown before pause (%)
MAX_DAILY_DRAWDOWN_PERCENT = 10

# =============================================================================
# API Rate Limits
# =============================================================================

# DexScreener
DEXSCREENER_RATE_LIMIT = None  # Unlimited (for now)

# GoPlus Security
GOPLUS_RATE_LIMIT_PER_MIN = 30
GOPLUS_RATE_LIMIT_PER_DAY = 43_200

# Moralis
MORALIS_FREE_TIER_CU_PER_DAY = 40_000

# Alchemy
ALCHEMY_FREE_TIER_CU_PER_MONTH = 100_000_000

# =============================================================================
# Time Constants
# =============================================================================

SECONDS_PER_DAY = 86_400
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30

# =============================================================================
# Data Collection
# =============================================================================

# How often to update open positions (minutes)
POSITION_UPDATE_INTERVAL_MIN = 5

# How often to discover new tokens (hours)
TOKEN_DISCOVERY_INTERVAL_HOURS = 1

# How often to check exit conditions (minutes)
EXIT_CHECK_INTERVAL_MIN = 1

# How long to cache API responses (seconds)
CACHE_DURATION_SECONDS = 300  # 5 minutes

# =============================================================================
# Backtesting
# =============================================================================

# Default backtesting period
DEFAULT_BACKTEST_DAYS = 90

# Minimum data points for backtesting
MIN_BACKTEST_DATA_POINTS = 100

# =============================================================================
# Slippage Protection (Modern 2025 Safety Features)
# =============================================================================

# Default slippage tolerances (percentage as decimal, e.g., 2.0 = 2%)
DEFAULT_SLIPPAGE_TOLERANCE = 2.0      # 2% default for most trades
MAX_SLIPPAGE_TOLERANCE = 5.0          # 5% absolute maximum (abort above this)
LOW_SLIPPAGE_TOLERANCE = 1.0          # 1% for high-quality pools (score >=90)
MEDIUM_SLIPPAGE_TOLERANCE = 3.0       # 3% for medium-quality pools (score 70-89)
HIGH_SLIPPAGE_ALERT_THRESHOLD = 3.0   # Alert user if estimated slippage >3%

# Dynamic slippage adjustment based on liquidity analysis results
SLIPPAGE_BY_POOL_QUALITY = {
    'LOW': 1.0,        # Low slippage pools: 1% tolerance
    'MEDIUM': 3.0,     # Medium slippage: 3% tolerance
    'HIGH': 5.0        # High slippage: 5% tolerance (or skip trade)
}

SLIPPAGE_BY_LIQUIDITY_SCORE = {
    'PASS': 2.0,       # Score >=80: 2% tolerance (high quality)
    'CAUTION': 3.0,    # Score 60-79: 3% tolerance (medium quality)
    'REJECT': None     # Score <60: Don't trade
}

# =============================================================================
# Pre-Execution Validation
# =============================================================================

# Liquidity validation thresholds
MIN_LIQUIDITY_RETENTION_RATIO = 0.5   # Abort if liquidity dropped >50% since discovery
LIQUIDITY_STALENESS_SECONDS = 300     # Re-validate if discovery data >5min old
MIN_LIQUIDITY_RECHECK_USD = 50_000    # Minimum liquidity required at execution time
LIQUIDITY_DROP_WARNING_PERCENT = 20   # Warn if liquidity dropped >20%
CRITICAL_LIQUIDITY_DROP_PERCENT = 50  # Critical alert if dropped >50%

# Pool reserve balance validation
MIN_RESERVE_RATIO = 0.3               # Minimum reserve ratio (reserve0/reserve1)
MAX_RESERVE_RATIO = 3.0               # Maximum reserve ratio (highly imbalanced)
RESERVE_IMBALANCE_WARNING = 2.0       # Warn if ratio > 2.0 or < 0.5

# =============================================================================
# Transaction Execution Parameters
# =============================================================================

# Transaction deadlines and timeouts
TX_DEADLINE_SECONDS = 300             # 5 minute transaction deadline from submission
MAX_PENDING_TX_TIME = 120             # Max time to wait for tx confirmation (2 min)
TX_RETRY_ATTEMPTS = 2                 # Number of times to retry failed transactions

# Gas settings for BSC
MAX_GAS_PRICE_GWEI = 10               # Maximum gas price on BSC (10 Gwei)
DEFAULT_GAS_LIMIT = 350_000           # Default gas limit for token swaps
GAS_ESTIMATE_BUFFER = 1.2             # Add 20% buffer to gas estimates
PRIORITY_GAS_MULTIPLIER = 1.5         # Increase gas by 50% for priority execution

# =============================================================================
# Emergency Circuit Breakers
# =============================================================================

# Conditions that will abort a trade before execution
ABORT_ON_HIGH_SLIPPAGE = True         # Abort if estimated slippage >MAX_SLIPPAGE_TOLERANCE
ABORT_ON_LIQUIDITY_DROP = True        # Abort if liquidity dropped >50% since discovery
ABORT_ON_STALE_DATA = True            # Abort if discovery data >5min old
ABORT_ON_RESERVE_IMBALANCE = True     # Abort if pool reserves highly imbalanced
ABORT_ON_INSUFFICIENT_LIQUIDITY = True  # Abort if current liquidity <MIN_LIQUIDITY_RECHECK_USD

# Warning conditions (log warning but don't abort)
WARN_ON_MODERATE_LIQUIDITY_DROP = True  # Warn if liquidity dropped 20-50%
WARN_ON_HIGH_ESTIMATED_SLIPPAGE = True  # Warn if estimated slippage 3-5%
WARN_ON_RESERVE_WARNING_LEVEL = True    # Warn if reserves moderately imbalanced

# =============================================================================
# On-Chain Query Settings
# =============================================================================

# RPC retry settings
RPC_RETRY_ATTEMPTS = 3                # Number of times to retry RPC calls
RPC_RETRY_DELAY_SECONDS = 1.0         # Delay between retries
RPC_TIMEOUT_SECONDS = 10              # Timeout for RPC requests

# Price quote settings
PRICE_QUOTE_STALENESS_SECONDS = 30    # Re-fetch price if quote >30 seconds old
MIN_PRICE_QUOTES = 2                  # Get multiple quotes and use median

# =============================================================================
# Validation Functions
# =============================================================================

def validate_constants():
    """Sanity check on constants"""
    # Original validations
    assert MIN_TOKEN_AGE_DAYS < MAX_TOKEN_AGE_DAYS, "Min age must be < max age"
    assert MIN_MARKET_CAP_USD < MAX_MARKET_CAP_USD, "Min mcap must be < max mcap"
    assert 0 <= MAX_GINI_COEFFICIENT <= 1, "Gini must be between 0 and 1"
    assert STOP_LOSS_PERCENT < 0, "Stop loss must be negative"
    assert TAKE_PROFIT_T1_PERCENT > 0, "Take profit must be positive"
    assert TAKE_PROFIT_T1_PERCENT < TAKE_PROFIT_T2_PERCENT, "TP1 must be < TP2"

    # Slippage validation
    assert 0 < DEFAULT_SLIPPAGE_TOLERANCE <= MAX_SLIPPAGE_TOLERANCE, "Default slippage must be <= max"
    assert MAX_SLIPPAGE_TOLERANCE <= 100, "Max slippage must be <= 100%"
    assert LOW_SLIPPAGE_TOLERANCE < MEDIUM_SLIPPAGE_TOLERANCE, "Low slippage must be < medium"

    # Pre-execution validation
    assert 0 < MIN_LIQUIDITY_RETENTION_RATIO <= 1.0, "Liquidity retention ratio must be 0-1"
    assert LIQUIDITY_STALENESS_SECONDS > 0, "Staleness must be positive"
    assert MIN_RESERVE_RATIO < MAX_RESERVE_RATIO, "Min reserve ratio must be < max"

    # Transaction params
    assert TX_DEADLINE_SECONDS > 0, "TX deadline must be positive"
    assert DEFAULT_GAS_LIMIT > 0, "Gas limit must be positive"
    assert GAS_ESTIMATE_BUFFER >= 1.0, "Gas buffer must be >= 1.0"

    print("✅ Constants validation passed")


if __name__ == "__main__":
    print("Super Pancake - Constants Test")
    print("=" * 60)
    print(f"Token Age Window: {MIN_TOKEN_AGE_DAYS}-{MAX_TOKEN_AGE_DAYS} days")
    print(f"Market Cap Window: ${MIN_MARKET_CAP_USD:,} - ${MAX_MARKET_CAP_USD:,}")
    print(f"Security: Min GoPlus Score = {MIN_GOPLUS_SCORE}, Max Gini = {MAX_GINI_COEFFICIENT}")
    print(f"Risk: Stop Loss = {STOP_LOSS_PERCENT}%, TP1 = {TAKE_PROFIT_T1_PERCENT}%, TP2 = {TAKE_PROFIT_T2_PERCENT}%")
    print(f"PancakeSwap Router: {PANCAKESWAP_ROUTER_V2}")
    print("=" * 60)
    validate_constants()
