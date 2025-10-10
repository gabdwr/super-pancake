# Super Pancake - Implementation Task List

**Last Updated:** 2025-10-08
**Project Duration:** 6-18 weeks (MVP + validation)
**Current Phase:** Not Started

---

## Task Status Legend
- ⬜ Not Started
- 🟦 In Progress
- ✅ Complete
- ❌ Blocked
- ⏸️ Paused

---

# Phase 1: Foundation & Setup (Week 1-2)

## 1.1 Environment Setup
- ⬜ **Task:** Install Python 3.10+ and verify installation
  - **Command:** `python3 --version`
  - **Expected:** Python 3.10 or higher

- ⬜ **Task:** Set up virtual environment
  - **Commands:**
    ```bash
    cd ~/Documents/super-pancake
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
  - **Why:** Isolates project dependencies from system Python

- ⬜ **Task:** Create project directory structure
  - **Action:** Copy structure from PROJECT_PLAN.md
  - **Verify:** All folders exist (src/, tests/, data/, config/, scripts/)

- ⬜ **Task:** Initialize Git repository (if not already done)
  - **Commands:**
    ```bash
    git init
    git add .
    git commit -m "Initial project structure"
    ```

## 1.2 Dependency Installation
- ⬜ **Task:** Create requirements.txt with core dependencies
  - **Contents:**
    ```
    web3>=6.0.0
    requests>=2.31.0
    pandas>=2.0.0
    numpy>=1.24.0
    psycopg2-binary>=2.9.0
    backtesting>=0.3.3
    python-telegram-bot>=20.0
    python-dotenv>=1.0.0
    flask>=3.0.0
    ta-lib>=0.4.0  # Technical indicators
    ```

- ⬜ **Task:** Install all dependencies
  - **Command:** `pip install -r requirements.txt`
  - **Troubleshooting:** If ta-lib fails, see: https://github.com/mrjbq7/ta-lib#installation

- ⬜ **Task:** Verify installations
  - **Test Script:**
    ```python
    import web3
    import requests
    import pandas
    import backtesting
    print("All imports successful!")
    ```

## 1.3 API Key Setup
- ⬜ **Task:** Sign up for DexScreener (no API key needed for basic endpoints)
  - **URL:** https://dexscreener.com/
  - **Test Endpoint:** `https://api.dexscreener.com/latest/dex/tokens/{address}`
  - **Store:** N/A (public API)

- ⬜ **Task:** No signup needed for GoPlus Security!
  - **URL:** https://gopluslabs.io/token-security-api (for reference/docs)
  - **Free Tier:** 30 calls/minute = 43,200/day (NO API KEY REQUIRED!)
  - **Authentication:** None required (`access_token=None`)
  - **Store:** Nothing to store - works without authentication
  - **Test:** Run `python scripts/test_goplus.py` to verify
  - **Higher Limits:** Contact service@gopluslabs.io if you need >30 calls/min

- ⬜ **Task:** Sign up for Moralis
  - **URL:** https://moralis.com/
  - **Free Tier:** 40K compute units/day
  - **Get API Key:** Dashboard → Settings → API Keys
  - **Store:** Add to `.env` file: `MORALIS_API_KEY=your_key_here`

- ⬜ **Task:** Sign up for Alchemy (BSC RPC endpoint)
  - **URL:** https://www.alchemy.com/
  - **Free Tier:** 100M compute units/month
  - **Get API Key:** Create app → Select "BNB Smart Chain"
  - **Store:** Add to `.env` file: `ALCHEMY_BSC_RPC=https://bnb-mainnet.g.alchemy.com/v2/YOUR_KEY`
  - **Alternative:** Use public BSC RPC: `https://bsc-dataseed.binance.org/`

- ⬜ **Task:** Create `.env` file in project root
  - **Template:**
    ```env
    # API Keys
    # GoPlus API - No key needed! Free tier: 30 calls/min (43,200/day)
    MORALIS_API_KEY=your_moralis_key
    ALCHEMY_BSC_RPC=your_alchemy_bsc_url

    # Telegram (optional for now)
    TELEGRAM_BOT_TOKEN=
    TELEGRAM_CHAT_ID=

    # Database (for later)
    DATABASE_URL=postgresql://localhost:5432/superpancake

    # Trading (paper trading settings)
    PAPER_TRADING_BALANCE=1000  # Starting balance in USDT
    MAX_POSITION_SIZE=50  # Max per trade in USDT
    ```

- ⬜ **Task:** Add `.env` to `.gitignore`
  - **Why:** Never commit API keys to Git!
  - **Command:** `echo ".env" >> .gitignore`

## 1.4 Configuration Files
- ⬜ **Task:** Create `config/settings.py`
  - **Purpose:** Load environment variables and app settings
  - **Code Template:**
    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # API Keys
    # GoPlus doesn't need an API key - free tier works without authentication
    MORALIS_API_KEY = os.getenv('MORALIS_API_KEY')
    ALCHEMY_BSC_RPC = os.getenv('ALCHEMY_BSC_RPC', 'https://bsc-dataseed.binance.org/')

    # Chain Configuration
    BSC_CHAIN_ID = 56
    BSC_EXPLORER = 'https://bscscan.com'

    # Trading Parameters
    PAPER_TRADING = True  # Always True until Phase 6
    STARTING_BALANCE = float(os.getenv('PAPER_TRADING_BALANCE', 1000))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 50))

    # Telegram (optional)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    ```

- ⬜ **Task:** Create `config/constants.py`
  - **Purpose:** Trading rules and filter thresholds
  - **Code Template:**
    ```python
    # Token Filter Criteria
    MIN_TOKEN_AGE_DAYS = 7
    MAX_TOKEN_AGE_DAYS = 30
    MIN_MARKET_CAP_USD = 500_000
    MAX_MARKET_CAP_USD = 5_000_000
    MIN_LIQUIDITY_USD = 50_000
    MIN_LIQUIDITY_LOCK_DAYS = 180  # 6 months

    # Security Thresholds
    MIN_GOPLUS_SCORE = 70  # Out of 100
    MAX_GINI_COEFFICIENT = 0.7  # Holder concentration
    MIN_VOLUME_LIQUIDITY_RATIO = 0.5
    MAX_VOLUME_LIQUIDITY_RATIO = 3.0

    # Risk Management
    STOP_LOSS_PERCENT = -50  # Cut at -50%
    TAKE_PROFIT_T1_PERCENT = 100  # First TP at +100%
    TAKE_PROFIT_T1_SIZE = 0.5  # Sell 50% at T1
    TAKE_PROFIT_T2_PERCENT = 300  # Second TP at +300%
    TAKE_PROFIT_T2_SIZE = 0.25  # Sell 25% at T2
    TRAILING_STOP_PERCENT = 30  # Trail remaining 25%

    # DEX Addresses (PancakeSwap V2)
    PANCAKESWAP_ROUTER_V2 = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
    PANCAKESWAP_FACTORY_V2 = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
    WBNB_ADDRESS = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
    USDT_ADDRESS = '0x55d398326f99059fF775485246999027B3197955'  # BSC USDT
    ```

## 1.5 Database Setup (PostgreSQL)
- ⬜ **Task:** Install PostgreSQL
  - **Linux:** `sudo apt-get install postgresql postgresql-contrib`
  - **Mac:** `brew install postgresql`
  - **Windows:** Download from https://www.postgresql.org/download/

- ⬜ **Task:** Create database
  - **Commands:**
    ```bash
    sudo -u postgres psql
    CREATE DATABASE superpancake;
    CREATE USER pancake_user WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE superpancake TO pancake_user;
    \q
    ```
  - **Update `.env`:** `DATABASE_URL=postgresql://pancake_user:your_password@localhost:5432/superpancake`

- ⬜ **Task:** Create `src/database/models.py`
  - **Purpose:** Database schema definitions
  - **Tables Needed:**
    - `tokens` - Discovered tokens with metadata
    - `security_checks` - GoPlus results over time
    - `price_history` - OHLCV data
    - `paper_trades` - Simulated trade log
    - `performance` - Daily portfolio snapshots

- ⬜ **Task:** Create database initialization script
  - **File:** `scripts/init_db.py`
  - **Action:** Run to create tables
  - **Verify:** `psql superpancake -c "\dt"` shows all tables

---

# Phase 2: Token Discovery (Week 2)

## 2.1 DexScreener Integration
- ⬜ **Task:** Create `src/discovery/dexscreener.py`
  - **Purpose:** Fetch new token listings from DexScreener
  - **Functions Needed:**
    - `get_latest_tokens(chain='bsc', limit=100)` - Get recent listings
    - `get_token_info(address)` - Detailed token data
    - `get_token_pairs(address)` - All trading pairs for a token
  - **API Endpoints:**
    - Latest: `https://api.dexscreener.com/latest/dex/search?q={symbol}`
    - Token: `https://api.dexscreener.com/latest/dex/tokens/{address}`
    - Pairs: `https://api.dexscreener.com/latest/dex/pairs/{chainId}/{pairAddress}`

- ⬜ **Task:** Implement rate limiting
  - **Why:** Avoid API bans
  - **Method:** Use `time.sleep()` between requests
  - **Rule:** Max 2 requests/second (conservative)

- ⬜ **Task:** Add caching layer
  - **Why:** Don't re-fetch same token multiple times
  - **Method:** Save responses to `data/cache/` with timestamp
  - **TTL:** 5 minutes for price data, 1 hour for metadata

- ⬜ **Task:** Test DexScreener integration
  - **Action:** Fetch 10 tokens and print details
  - **Verify:** See token address, name, age, market cap, liquidity

## 2.2 Token Age Filter
- ⬜ **Task:** Create `src/discovery/filters.py`
  - **Purpose:** Filter tokens by age, market cap, liquidity

- ⬜ **Task:** Implement `calculate_token_age()`
  - **Input:** Token creation timestamp or first DEX listing time
  - **Output:** Age in days (float)
  - **Source:** DexScreener `pairCreatedAt` field

- ⬜ **Task:** Implement `filter_by_age()`
  - **Logic:**
    ```python
    MIN_TOKEN_AGE_DAYS <= age <= MAX_TOKEN_AGE_DAYS
    ```
  - **Return:** Boolean (pass/fail)

- ⬜ **Task:** Implement `filter_by_market_cap()`
  - **Input:** Market cap in USD
  - **Logic:**
    ```python
    MIN_MARKET_CAP_USD <= market_cap <= MAX_MARKET_CAP_USD
    ```

- ⬜ **Task:** Implement `filter_by_liquidity()`
  - **Input:** Total liquidity in USD across all pairs
  - **Logic:**
    ```python
    liquidity >= MIN_LIQUIDITY_USD
    ```

- ⬜ **Task:** Create master filter pipeline
  - **Function:** `apply_basic_filters(token_data)`
  - **Returns:** `(passed: bool, reasons: list)`
  - **Log:** Why tokens fail (for debugging)

## 2.3 Data Storage
- ⬜ **Task:** Create `src/database/queries.py`
  - **Functions:**
    - `insert_token(token_data)` - Add new token
    - `update_token(address, updates)` - Update existing
    - `get_token(address)` - Retrieve by address
    - `get_tokens_by_age(min_days, max_days)` - Query by age
    - `token_exists(address)` - Check if already tracked

- ⬜ **Task:** Implement duplicate detection
  - **Why:** Don't process same token multiple times
  - **Method:** Check `tokens` table before inserting
  - **Action:** If exists, update timestamp and price

- ⬜ **Task:** Create discovery logging
  - **File:** `logs/discovery.log`
  - **Format:** `[timestamp] [level] [token_address] message`
  - **Track:** Tokens discovered, filtered out, added to DB

---

# Phase 3: Security Screening (Week 3)

## 3.1 GoPlus Security API
- ⬜ **Task:** Create `src/analysis/security.py`
  - **Purpose:** Automated scam detection via GoPlus

- ⬜ **Task:** Implement `check_token_security(address, chain='bsc')`
  - **API Endpoint:**
    ```
    https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={address}
    ```
  - **Auth:** None required! Free tier works without authentication
  - **Example:**
    ```python
    import requests

    def check_token_security(address, chain='56'):  # 56 = BSC
        url = f"https://api.gopluslabs.io/api/v1/token_security/{chain}"
        params = {"contract_addresses": address}
        response = requests.get(url, params=params)
        return response.json()
    ```
  - **Response Fields:**
    - `is_open_source` - Is contract verified?
    - `is_proxy` - Can owner change logic?
    - `is_mintable` - Can owner create new tokens?
    - `can_take_back_ownership` - Renounced ownership?
    - `owner_address` - Who controls the contract?
    - `owner_balance` - How much does owner hold?
    - `holder_count` - Number of unique holders
    - `lp_holder_count` - Liquidity providers
    - `is_honeypot` - Can you sell after buying?
    - `honeypot_with_same_creator` - Creator's history
    - `trading_cooldown` - Forced wait between trades?

- ⬜ **Task:** Implement `calculate_security_score(goplus_data)`
  - **Scoring Logic:**
    ```python
    score = 100
    if not is_open_source: score -= 30
    if is_proxy: score -= 20
    if is_mintable: score -= 15
    if can_take_back_ownership: score -= 15
    if is_honeypot: score = 0  # Auto-fail
    if owner_balance > 0.1: score -= 10  # Owner holds >10%
    if holder_count < 100: score -= 10
    return max(0, score)
    ```

- ⬜ **Task:** Implement red flag detection
  - **Function:** `get_security_red_flags(goplus_data)`
  - **Returns:** List of human-readable warnings
  - **Examples:**
    - "⚠️ Contract is not verified"
    - "🚨 HONEYPOT DETECTED - Cannot sell!"
    - "⚠️ Owner can mint unlimited tokens"
    - "⚠️ Ownership not renounced"

- ⬜ **Task:** Add security check to database
  - **Table:** `security_checks`
  - **Fields:** `token_address`, `checked_at`, `score`, `red_flags` (JSON), `raw_response` (JSON)
  - **Why:** Track how security changes over time

## 3.2 Holder Distribution Analysis
- ⬜ **Task:** Create `src/analysis/holders.py`

- ⬜ **Task:** Implement `get_holder_list(address)` using Moralis
  - **API Endpoint:**
    ```
    https://deep-index.moralis.io/api/v2/erc20/{address}/owners
    ```
  - **Headers:** `X-API-Key: {MORALIS_API_KEY}`
  - **Params:** `chain=bsc`, `limit=100` (get top holders)
  - **Response:** List of `{owner_address, balance, percentage}`

- ⬜ **Task:** Implement `calculate_gini_coefficient(balances)`
  - **What:** Measures inequality (0=equal, 1=one person owns all)
  - **Formula:**
    ```python
    import numpy as np
    def gini(balances):
        sorted_balances = np.sort(balances)
        n = len(balances)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_balances)) / (n * np.sum(sorted_balances)) - (n + 1) / n
    ```
  - **Interpretation:**
    - <0.5 = Very distributed (good)
    - 0.5-0.7 = Moderate concentration (acceptable)
    - >0.7 = High concentration (risky - whales can dump)

- ⬜ **Task:** Implement `check_whale_wallets(holders)`
  - **Logic:** Flag if any single wallet holds >20%
  - **Exclude:** Known DEX/CEX wallets (PancakeSwap, Binance hot wallets)
  - **Return:** `(has_whales: bool, whale_addresses: list)`

- ⬜ **Task:** Implement `analyze_holder_growth(address, days=7)`
  - **Challenge:** Requires historical snapshots (not available via API)
  - **Workaround:** Track holder count over time in your own DB
  - **Future Enhancement:** Scrape BSCScan holder history

## 3.3 Volume Analysis (Wash Trading Detection)
- ⬜ **Task:** Create `src/analysis/volume.py`

- ⬜ **Task:** Implement `get_volume_stats(address, timeframe='24h')`
  - **Source:** DexScreener API (`volume` field in pair data)
  - **Return:**
    ```python
    {
        'volume_24h': float,
        'liquidity': float,
        'ratio': volume / liquidity,
        'num_txns': int,
        'avg_txn_size': volume / num_txns
    }
    ```

- ⬜ **Task:** Implement `detect_wash_trading(volume_stats)`
  - **Red Flags:**
    - Volume/Liquidity ratio >5x (too much activity for pool size)
    - Very high transaction count but low unique addresses
    - Repetitive transaction sizes (bots trading with themselves)
  - **Return:** `(is_suspicious: bool, confidence: float, reasons: list)`

- ⬜ **Task:** Implement `check_volume_consistency(address, days=7)`
  - **Purpose:** Detect sudden volume spikes (pump signals)
  - **Logic:** Compare today's volume to 7-day average
  - **Red Flag:** >10x spike (likely coordinated pump)

## 3.4 Composite Scoring System
- ⬜ **Task:** Create `src/analysis/scoring.py`

- ⬜ **Task:** Implement `calculate_composite_score(token)`
  - **Inputs:**
    - Security score (GoPlus)
    - Gini coefficient
    - Volume/liquidity ratio
    - Holder count
    - Liquidity lock duration
  - **Weights:**
    ```python
    composite_score = (
        security_score * 0.40 +  # Most important
        (1 - gini) * 100 * 0.20 +  # Distribution matters
        volume_health * 0.15 +  # Organic activity
        holder_score * 0.15 +  # Community size
        liquidity_lock_score * 0.10  # Rug protection
    )
    ```
  - **Return:** Score 0-100

- ⬜ **Task:** Implement `rank_tokens(token_list)`
  - **Purpose:** Sort by composite score (best first)
  - **Return:** Sorted list with scores

- ⬜ **Task:** Add scoring to database
  - **Table:** Update `tokens` table with `composite_score` column
  - **Refresh:** Recalculate daily (scores change as data updates)

---

# Phase 4: Backtesting Engine (Week 4)

## 4.1 Historical Data Collection
- ⬜ **Task:** Create `data/historical/` folder

- ⬜ **Task:** Download sample data from CryptoDataDownload
  - **URL:** https://www.cryptodatadownload.com/data/binance/
  - **Format:** CSV with columns: `timestamp, open, high, low, close, volume`
  - **Tokens:** Get 10-20 established BSC tokens for testing
  - **Save:** `data/historical/{token_symbol}_USDT_1h.csv`

- ⬜ **Task:** Create `src/backtest/data_loader.py`
  - **Function:** `load_csv_data(file_path)`
  - **Processing:**
    - Parse timestamp to datetime
    - Set datetime as index
    - Ensure OHLCV columns are float
    - Handle missing values (forward fill or drop)
  - **Return:** pandas DataFrame

- ⬜ **Task:** Implement `fetch_historical_from_api(address, days=90)`
  - **Challenge:** Free APIs have limited history
  - **Sources to try:**
    - Moralis (limited)
    - DexScreener (very limited)
    - CoinGecko (requires paid tier for most tokens)
  - **Fallback:** Use prospectively collected data (Phase 6)

## 4.2 Backtesting.py Integration
- ⬜ **Task:** Create `src/backtest/engine.py`

- ⬜ **Task:** Implement basic strategy class
  - **Code Template:**
    ```python
    from backtesting import Strategy

    class BuyAndHoldStrategy(Strategy):
        def init(self):
            pass  # Initialize indicators here

        def next(self):
            if not self.position:
                self.buy()  # Simple: buy at start, hold forever
    ```

- ⬜ **Task:** Implement 7-day entry strategy
  - **Name:** `SevenDayEntryStrategy`
  - **Logic:**
    - Wait until token is 7 days old
    - Enter position if:
      - Security score >70
      - Gini <0.7
      - Volume/liquidity ratio 0.5-3x
    - Hold for 30 days or until stop loss/take profit

- ⬜ **Task:** Implement risk management in strategy
  - **Stop Loss:** Exit if price drops 50% from entry
  - **Take Profit T1:** Sell 50% at +100% gain
  - **Take Profit T2:** Sell 25% at +300% gain
  - **Trailing Stop:** Trail remaining 25% with 30% stop

- ⬜ **Task:** Create backtest runner script
  - **File:** `scripts/run_backtest.py`
  - **Usage:** `python scripts/run_backtest.py --strategy 7day --data data/historical/`
  - **Output:** Performance stats + HTML report

## 4.3 Performance Metrics
- ⬜ **Task:** Implement `src/backtest/metrics.py`

- ⬜ **Task:** Calculate standard metrics
  - **Functions:**
    - `calculate_win_rate(trades)` - % of profitable trades
    - `calculate_avg_winner(trades)` - Mean % gain on winners
    - `calculate_avg_loser(trades)` - Mean % loss on losers
    - `calculate_expected_value(win_rate, avg_win, avg_loss)`
    - `calculate_sharpe_ratio(returns, risk_free_rate=0.02)`
    - `calculate_max_drawdown(equity_curve)`
    - `calculate_profit_factor(gross_profit, gross_loss)`

- ⬜ **Task:** Create performance report generator
  - **Function:** `generate_backtest_report(results)`
  - **Output:** Markdown file with:
    - Strategy parameters
    - Performance metrics table
    - Equity curve chart
    - Trade list with entry/exit/P&L
    - Red flags/lessons learned

- ⬜ **Task:** Implement survivorship bias warning
  - **Why:** Backtesting on survivors overstates performance
  - **Solution:** Track how many tokens were filtered out vs. actually traded
  - **Report:** "Backtest includes X winners, Y losers, but excludes Z rugged/dead tokens"

---

# Phase 5: Paper Trading System (Week 5)

## 5.1 Web3 Setup (BSC Connection)
- ⬜ **Task:** Create `src/trading/web3_connection.py`

- ⬜ **Task:** Implement BSC connection
  - **Code Template:**
    ```python
    from web3 import Web3
    from config.settings import ALCHEMY_BSC_RPC, BSC_CHAIN_ID

    w3 = Web3(Web3.HTTPProvider(ALCHEMY_BSC_RPC))

    def is_connected():
        return w3.is_connected()

    def get_block_number():
        return w3.eth.block_number

    def get_gas_price():
        return w3.eth.gas_price
    ```

- ⬜ **Task:** Test connection
  - **Script:** `python -c "from src.trading.web3_connection import *; print(f'Connected: {is_connected()}, Block: {get_block_number()}')"`
  - **Expected:** `Connected: True, Block: 43284719` (or current block)

## 5.2 PancakeSwap Integration
- ⬜ **Task:** Create `src/trading/dex_interface.py`

- ⬜ **Task:** Load PancakeSwap Router ABI
  - **Source:** https://bscscan.com/address/0x10ED43C718714eb63d5aA57B78B54704E256024E#code
  - **Save:** `config/abis/pancakeswap_router_v2.json`
  - **Load:**
    ```python
    import json
    with open('config/abis/pancakeswap_router_v2.json') as f:
        router_abi = json.load(f)
    ```

- ⬜ **Task:** Implement `get_token_price(token_address, quote='USDT')`
  - **Method:** Call PancakeSwap `getAmountsOut()`
  - **Logic:** How much USDT for 1 token?
  - **Handle:** Tokens with different decimals (most are 18, but check)

- ⬜ **Task:** Implement `simulate_buy(token_address, amount_usdt, slippage=3)`
  - **Purpose:** Calculate what you'd get WITHOUT executing
  - **Method:**
    - Get current price
    - Apply slippage: `effective_price = price * (1 + slippage/100)`
    - Calculate tokens received: `amount_usdt / effective_price`
    - Deduct DEX fee (0.25% on PancakeSwap v2)
  - **Return:** `(tokens_received, effective_price, gas_estimate)`

- ⬜ **Task:** Implement `simulate_sell(token_address, amount_tokens, slippage=3)`
  - **Similar to buy but reverse direction**

- ⬜ **Task:** Get gas cost estimates
  - **Method:** `w3.eth.estimate_gas(transaction)`
  - **Typical:** 150,000-200,000 gas for swap
  - **Cost:** `gas_used * gas_price` in BNB
  - **Convert:** BNB price to USD for P&L tracking

## 5.3 Paper Trading Engine
- ⬜ **Task:** Create `src/trading/paper_trader.py`

- ⬜ **Task:** Implement `PaperTradingAccount` class
  - **Attributes:**
    ```python
    self.balance_usdt = starting_balance  # e.g., 1000
    self.positions = {}  # {token_address: {amount, entry_price, entry_time}}
    self.trade_history = []  # List of completed trades
    self.total_gas_paid = 0  # Track costs
    ```

- ⬜ **Task:** Implement `paper_buy(token_address, amount_usdt)`
  - **Steps:**
    1. Check sufficient balance
    2. Call `simulate_buy()` to get price/slippage
    3. Deduct USDT from balance
    4. Add tokens to `positions`
    5. Log trade to `trade_history`
    6. Add gas cost to `total_gas_paid`
    7. Update database (`paper_trades` table)

- ⬜ **Task:** Implement `paper_sell(token_address, amount_tokens)`
  - **Similar to buy but reverse**
  - **Calculate P&L:** `(exit_price - entry_price) / entry_price * 100`

- ⬜ **Task:** Implement `update_positions()`
  - **Purpose:** Refresh current prices for open positions
  - **Run:** Every 5 minutes via cron job
  - **Output:** Unrealized P&L for each position

- ⬜ **Task:** Implement automatic exits (stop loss / take profit)
  - **Function:** `check_exit_conditions()`
  - **For each open position:**
    - If price <= entry_price * 0.5 → Stop loss
    - If price >= entry_price * 2.0 → Take profit T1 (sell 50%)
    - If price >= entry_price * 4.0 → Take profit T2 (sell 25%)
    - If price drops 30% from peak → Trailing stop (sell remaining)

## 5.4 P&L Tracking & Reporting
- ⬜ **Task:** Create `src/trading/performance.py`

- ⬜ **Task:** Implement `calculate_portfolio_value()`
  - **Formula:**
    ```python
    total = balance_usdt
    for position in positions.values():
        current_price = get_token_price(position['address'])
        total += position['amount'] * current_price
    return total
    ```

- ⬜ **Task:** Implement daily snapshot
  - **Function:** `save_daily_performance()`
  - **Table:** `performance` (date, total_value, realized_pnl, unrealized_pnl)
  - **Schedule:** Run at midnight UTC via cron

- ⬜ **Task:** Create performance dashboard
  - **Options:**
    - Simple: CSV export + Google Sheets
    - Medium: Flask web app with charts
    - Advanced: Streamlit dashboard
  - **Metrics to show:**
    - Current portfolio value
    - Total P&L (%)
    - Win rate
    - Best/worst trades
    - Open positions with unrealized P&L

---

# Phase 6: Cloud Deployment (Week 6)

## 6.1 VPS Setup (DigitalOcean)
- ⬜ **Task:** Sign up for DigitalOcean
  - **URL:** https://www.digitalocean.com/
  - **Promo:** Search for "$200 credit" signup offers

- ⬜ **Task:** Create Droplet
  - **Image:** Ubuntu 22.04 LTS
  - **Plan:** Basic ($4/month - 512MB RAM)
  - **Datacenter:** Choose closest to you
  - **SSH Key:** Add your public key for authentication

- ⬜ **Task:** Initial server setup
  - **Connect:** `ssh root@your_droplet_ip`
  - **Update:**
    ```bash
    apt update && apt upgrade -y
    apt install python3-pip python3-venv postgresql git -y
    ```
  - **Create user:**
    ```bash
    adduser pancake
    usermod -aG sudo pancake
    su - pancake
    ```

- ⬜ **Task:** Clone repository to VPS
  - **Commands:**
    ```bash
    cd ~
    git clone https://github.com/yourusername/super-pancake.git
    cd super-pancake
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

- ⬜ **Task:** Copy `.env` file to VPS
  - **Method:** `scp .env pancake@your_droplet_ip:~/super-pancake/.env`
  - **Security:** Ensure file permissions: `chmod 600 .env`

- ⬜ **Task:** Setup PostgreSQL on VPS
  - **Commands:**
    ```bash
    sudo -u postgres createdb superpancake
    sudo -u postgres createuser pancake_user
    sudo -u postgres psql -c "ALTER USER pancake_user PASSWORD 'your_password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE superpancake TO pancake_user;"
    ```
  - **Initialize:** `python scripts/init_db.py`

## 6.2 Background Process Management
- ⬜ **Task:** Install screen or tmux
  - **Command:** `sudo apt install screen`
  - **Why:** Keep processes running after SSH disconnect

- ⬜ **Task:** Create startup script
  - **File:** `scripts/start_bot.sh`
  - **Contents:**
    ```bash
    #!/bin/bash
    cd ~/super-pancake
    source venv/bin/activate
    python scripts/main_loop.py >> logs/bot.log 2>&1
    ```
  - **Make executable:** `chmod +x scripts/start_bot.sh`

- ⬜ **Task:** Run bot in screen session
  - **Commands:**
    ```bash
    screen -S pancake-bot
    ./scripts/start_bot.sh
    # Press Ctrl+A, then D to detach
    ```
  - **Reattach:** `screen -r pancake-bot`

- ⬜ **Task:** Setup systemd service (better than screen)
  - **File:** `/etc/systemd/system/pancake-bot.service`
  - **Contents:**
    ```ini
    [Unit]
    Description=Super Pancake Trading Bot
    After=network.target

    [Service]
    Type=simple
    User=pancake
    WorkingDirectory=/home/pancake/super-pancake
    ExecStart=/home/pancake/super-pancake/venv/bin/python /home/pancake/super-pancake/scripts/main_loop.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
  - **Commands:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable pancake-bot
    sudo systemctl start pancake-bot
    sudo systemctl status pancake-bot
    ```

## 6.3 Cron Jobs (Scheduled Tasks)
- ⬜ **Task:** Create cron schedule file
  - **Edit:** `crontab -e`
  - **Add:**
    ```cron
    # Discover new tokens every hour
    0 * * * * cd ~/super-pancake && venv/bin/python scripts/discover_tokens.py >> logs/discovery.log 2>&1

    # Update open positions every 5 minutes
    */5 * * * * cd ~/super-pancake && venv/bin/python scripts/update_positions.py >> logs/positions.log 2>&1

    # Check exit conditions every minute (for paper trading)
    * * * * * cd ~/super-pancake && venv/bin/python scripts/check_exits.py >> logs/exits.log 2>&1

    # Daily performance snapshot at midnight
    0 0 * * * cd ~/super-pancake && venv/bin/python scripts/daily_snapshot.py >> logs/performance.log 2>&1

    # Weekly report every Sunday at 6 PM
    0 18 * * 0 cd ~/super-pancake && venv/bin/python scripts/weekly_report.py >> logs/reports.log 2>&1
    ```

## 6.4 Telegram Alerts (Optional)
- ⬜ **Task:** Create Telegram bot
  - **Steps:**
    1. Message @BotFather on Telegram
    2. Send `/newbot`
    3. Follow prompts (name, username)
    4. Copy bot token to `.env`: `TELEGRAM_BOT_TOKEN=...`

- ⬜ **Task:** Get your chat ID
  - **Steps:**
    1. Message your bot
    2. Visit: `https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates`
    3. Find `"chat":{"id":123456789}`
    4. Add to `.env`: `TELEGRAM_CHAT_ID=123456789`

- ⬜ **Task:** Create `src/utils/alerts.py`
  - **Function:** `send_telegram_alert(message)`
  - **Use Cases:**
    - New token passed all filters
    - Paper trade executed (buy/sell)
    - Stop loss / take profit triggered
    - Daily P&L summary
    - Critical errors (API down, DB connection lost)

- ⬜ **Task:** Test alerts
  - **Command:** `python -c "from src.utils.alerts import send_telegram_alert; send_telegram_alert('🥞 Bot is live!')"`

## 6.5 Monitoring & Logging
- ⬜ **Task:** Setup log rotation
  - **Why:** Prevent logs from filling disk
  - **File:** `/etc/logrotate.d/pancake-bot`
  - **Contents:**
    ```
    /home/pancake/super-pancake/logs/*.log {
        daily
        rotate 14
        compress
        delaycompress
        missingok
        notifempty
    }
    ```

- ⬜ **Task:** Create health check script
  - **File:** `scripts/health_check.py`
  - **Checks:**
    - Is bot process running?
    - Database connection OK?
    - Last token discovery < 2 hours ago?
    - API keys working?
  - **Alert:** Send Telegram message if any check fails

- ⬜ **Task:** Setup monitoring dashboard (optional)
  - **Simple:** Use UptimeRobot (free) to ping a `/health` endpoint
  - **Advanced:** Deploy Grafana + Prometheus for metrics

---

# Phase 7: Validation & Iteration (Weeks 7-18)

## 7.1 Data Collection (Prospective)
- ⬜ **Task:** Let bot run for 30 days without trading
  - **Goal:** Collect data on tokens discovered
  - **Track:** Which tokens passed filters, how they performed

- ⬜ **Task:** Build historical dataset
  - **Script:** `scripts/build_historical_db.py`
  - **Method:** Every day, save OHLCV for tokens in database
  - **Storage:** `price_history` table
  - **Use:** After 90 days, you'll have real backtest data!

## 7.2 Paper Trading (60-90 Days)
- ⬜ **Task:** Enable paper trading
  - **Config:** `PAPER_TRADING = True` (should already be set)
  - **Start:** Let bot make trades based on strategy

- ⬜ **Task:** Weekly review meetings (with yourself)
  - **Questions:**
    - How many tokens passed filters this week?
    - How many paper trades were executed?
    - What's the win rate so far?
    - Which filters removed the most tokens?
    - Did any "failed" tokens actually moon? (false negatives)
    - Did any "passed" tokens rugpull? (false positives)

- ⬜ **Task:** Adjust filters based on results
  - **Example:** If win rate <20%, tighten filters (raise security score threshold)
  - **Example:** If zero trades in 2 weeks, loosen filters (lower market cap minimum)

- ⬜ **Task:** Track false positives/negatives
  - **False Positive:** Token passed filters but rugged/died
    - **Action:** Analyze why filters missed it, improve logic
  - **False Negative:** Token failed filters but 10x'd
    - **Action:** Was it a fluke or did filters remove something valuable?

## 7.3 Strategy Optimization
- ⬜ **Task:** A/B test entry timing
  - **Variants:**
    - A: 7-day entry (current)
    - B: 14-day entry (more conservative)
    - C: 5-day entry (more aggressive)
  - **Method:** Split capital 33%/33%/33%, compare after 60 days

- ⬜ **Task:** Test different exit strategies
  - **Variants:**
    - A: Current (50% stop, 100%/300% TP)
    - B: Tighter stop (30% stop, 50%/200% TP)
    - C: Let winners run (30% stop, 200%/500% TP)

- ⬜ **Task:** Backtest on collected data
  - **After 90 days:** You have real data!
  - **Run:** `scripts/run_backtest.py --data prospective`
  - **Compare:** Backtest results vs. actual paper trading

## 7.4 Decision Point (Month 4)
- ⬜ **Task:** Calculate actual performance metrics
  - **Metrics:**
    - Win rate
    - Average winner / average loser
    - Expected value
    - Sharpe ratio
    - Max drawdown
    - Total paper P&L

- ⬜ **Task:** Honest assessment
  - **Questions:**
    - Is win rate >25%? (Minimum for viability)
    - Is EV positive? (Otherwise you lose money long-term)
    - Is Sharpe ratio >0.5? (Bare minimum risk-adjusted return)
    - Can you mentally handle the drawdowns?
    - Are results better than just holding BNB/ETH?

- ⬜ **Task:** Make decision
  - **Option A: Proceed to real capital**
    - If: Win rate >30%, EV >20%, Sharpe >1.0
    - Action: Start with £250-500 (5-10% of intended bankroll)
  - **Option B: Iterate further**
    - If: Win rate 20-30%, EV slightly positive
    - Action: Refine filters, test another 60 days
  - **Option C: Pivot or abandon**
    - If: Win rate <20%, EV negative after 90 days
    - Action: Analyze why, consider new strategy or different market

---

# Phase 8: Real Capital (Month 7+) - ONLY IF VALIDATED

## 8.1 Pre-Launch Checklist
- ⬜ **Task:** Re-verify all security
  - **Check:** No API keys in Git
  - **Check:** VPS firewall configured (only SSH/HTTPS open)
  - **Check:** Database backups enabled
  - **Check:** 2FA on all exchange accounts

- ⬜ **Task:** Setup cold storage wallet
  - **Why:** Don't keep all funds in hot wallet
  - **Method:** MetaMask (hot) + Hardware Wallet (cold)
  - **Rule:** Only transfer needed capital to trading wallet

- ⬜ **Task:** Create emergency stop
  - **Function:** `emergency_stop()` - Sell all positions, stop bot
  - **Trigger:** Manual command or circuit breaker conditions
  - **Test:** Ensure it works in paper trading first

## 8.2 Small Capital Test (£250-500)
- ⬜ **Task:** Fund BSC wallet
  - **Send:** £250-500 equivalent USDT to MetaMask on BSC
  - **Bridge:** Use Binance or official BSC bridge

- ⬜ **Task:** Enable real trading (with safeguards)
  - **Config change:** `PAPER_TRADING = False`
  - **Add limits:**
    ```python
    MAX_TOTAL_CAPITAL = 500  # Hard cap
    MAX_OPEN_POSITIONS = 3  # Start small
    MAX_DAILY_TRADES = 5  # Prevent runaway bot
    ```

- ⬜ **Task:** Execute first real trade
  - **Monitor:** Watch transaction on BSCScan
  - **Verify:** Trade executed as expected, gas costs reasonable
  - **Document:** Actual slippage vs. simulated

- ⬜ **Task:** Run for 30 days
  - **Track:** Real P&L vs. paper trading projections
  - **Journal:** Note differences (slippage, failed txns, MEV)

## 8.3 Scaling Decision
- ⬜ **Task:** Compare real vs. paper results
  - **Key Metric:** Did real trading match paper trading within 20%?
  - **If worse:** Identify why (slippage? MEV? Execution timing?)
  - **If similar:** Consider scaling up

- ⬜ **Task:** Scale gradually
  - **Don't:** Jump from £500 to £5000
  - **Do:** Increase 50% every 60 days if profitable
  - **Example:** £500 → £750 → £1125 → £1700 over 6 months

- ⬜ **Task:** Set risk limits
  - **Max Drawdown:** If portfolio drops 30%, pause and review
  - **Max Loss Per Month:** If down 20% in 30 days, stop trading
  - **Max Capital:** Never risk more than you can afford to lose

---

# Ongoing Maintenance Tasks

## Daily
- ⬜ Check bot is running (`systemctl status pancake-bot`)
- ⬜ Review Telegram alerts for critical issues
- ⬜ Glance at open positions (unrealized P&L)

## Weekly
- ⬜ Review trade log (what was bought/sold, why)
- ⬜ Check filter statistics (how many tokens passed/failed)
- ⬜ Read about any major BSC/crypto news (market regime changes)
- ⬜ Update dependencies (`pip list --outdated`)

## Monthly
- ⬜ Calculate performance metrics (win rate, EV, Sharpe)
- ⬜ Review false positives/negatives
- ⬜ Consider filter adjustments
- ⬜ Backup database (`pg_dump superpancake > backup_$(date +%Y%m%d).sql`)
- ⬜ Review VPS costs and optimization opportunities

## Quarterly
- ⬜ Major strategy review
- ⬜ Consider adding new chains (Polygon, Base)
- ⬜ Research new data sources or APIs
- ⬜ Update documentation based on learnings

---

# Success Milestones

## 🎯 Phase 1-2 Complete (Week 2)
- ✅ Bot can discover tokens via DexScreener
- ✅ Basic filters working (age, market cap, liquidity)
- ✅ Data saved to PostgreSQL
- **Celebration:** You have a functional discovery system!

## 🎯 Phase 3 Complete (Week 3)
- ✅ GoPlus security checks integrated
- ✅ Holder distribution analysis working
- ✅ Composite scoring ranks tokens
- **Celebration:** You can automatically identify scams!

## 🎯 Phase 4 Complete (Week 4)
- ✅ Backtest runs on historical data
- ✅ Performance metrics calculated
- ✅ Strategy has positive EV (in backtest)
- **Celebration:** You have a testable strategy!

## 🎯 Phase 5 Complete (Week 5)
- ✅ Paper trading executes simulated trades
- ✅ P&L tracking works
- ✅ Exit conditions trigger correctly
- **Celebration:** You're virtually trading!

## 🎯 Phase 6 Complete (Week 6)
- ✅ Bot running 24/7 on VPS
- ✅ Cron jobs executing on schedule
- ✅ Telegram alerts working
- **Celebration:** Fully autonomous system!

## 🎯 Phase 7 Complete (Month 4)
- ✅ 90+ days of prospective data collected
- ✅ Paper trading win rate >30%
- ✅ Expected value >20%
- **Celebration:** Your strategy is validated!

## 🎯 Phase 8 Complete (Month 7+)
- ✅ Real capital test completed
- ✅ Actual results match paper trading
- ✅ Scaling plan in place
- **Celebration:** You built a real trading system!

---

# Red Flags to Watch For

## 🚨 During Development
- **No tokens pass filters for 2 weeks** → Filters too strict
- **100+ tokens pass filters per day** → Filters too loose (won't be able to analyze all)
- **GoPlus API always returns errors** → Check API key, rate limits
- **Can't connect to BSC** → RPC endpoint issue

## 🚨 During Paper Trading
- **Win rate <15% after 30 trades** → Strategy fundamentally broken
- **All winners are <2x, but losers are -50%+** → Risk/reward imbalanced
- **No trades executed in 2 weeks** → Discovery system not finding opportunities
- **Many tokens rug despite passing filters** → Security checks insufficient

## 🚨 During Real Trading
- **Actual slippage 5-10x higher than simulated** → Position size too large for liquidity
- **Frequent failed transactions** → Gas price too low or front-running
- **Real P&L 50%+ worse than paper trading** → Execution issues (MEV, timing, slippage)
- **Bot uses 100% of API rate limits** → Need paid tier or optimize calls

---

# Emergency Procedures

## 🆘 Bot Crashes
1. Check systemd status: `systemctl status pancake-bot`
2. Read last 50 log lines: `tail -n 50 logs/bot.log`
3. Look for Python errors (stack trace)
4. Restart: `systemctl restart pancake-bot`
5. If persistent: Comment out new code, redeploy

## 🆘 Token Rugs While You're Holding
1. **Don't panic** - This will happen with small caps
2. Check if you can still sell (GoPlus `is_honeypot`)
3. If sellable: Execute emergency sell (accept 50%+ slippage)
4. If honeypot: Write off as loss, document for future filter improvement
5. Review: Why did filters miss this? Update logic.

## 🆘 Lost Money on First Real Trade
1. **Expected** - First trades are learning experiences
2. Calculate: Was loss within expected range (50% stop loss)?
3. Analyze: Execution issue or strategy issue?
4. Document: Add to lessons learned
5. Don't scale capital until you understand why

## 🆘 VPS Compromised
1. Immediately: Stop bot, disconnect network
2. Check: Any unauthorized transactions?
3. Rotate: All API keys, database passwords
4. Rebuild: Fresh droplet, restore from backup
5. Review: How did breach occur? (SSH key leaked? Weak password?)

---

# Resources for Troubleshooting

## Documentation
- **Web3.py:** https://web3py.readthedocs.io/
- **BSCScan API:** https://docs.bscscan.com/
- **PancakeSwap Docs:** https://docs.pancakeswap.finance/
- **Backtesting.py:** https://kernc.github.io/backtesting.py/

## Communities
- **r/algotrading** - Systematic trading strategies
- **r/CryptoMoonShots** - See what manual traders look for
- **BSC Telegram** - Real-time market sentiment
- **Stack Overflow** - Python/Web3 technical issues

## Tools
- **BSCScan** - Verify transactions, check contracts
- **DexScreener** - Manual token research
- **GoPlus Security Web UI** - Verify API results
- **CoinGecko** - Market cap validation

---

**Remember:** This is a marathon, not a sprint. Take it one task at a time, document what you learn, and iterate based on real results. Most importantly: **Never risk more than you can afford to lose.**

Good luck! 🥞🚀
