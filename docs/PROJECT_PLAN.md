# Super Pancake - Crypto Token Analysis & Trading Bot

## 🎯 Project Overview

A systematic tool to discover and analyze new cryptocurrency tokens in the 7-30 day "sweet spot" - after initial launch chaos but before mainstream discovery. Uses free APIs to screen tokens on Binance Smart Chain (BSC) for security risks, then paper trades to validate strategies before risking real capital.

**Target Entry Window:** 7-30 days after token launch
**Target Market Cap:** $500K - $5M
**Expected Win Rate:** 32% (based on 2024 backtest data)
**Monthly Infrastructure Cost:** £4-15
**Test Trade Size:** £10-50 on BSC (low gas fees)

---

## 📚 Resources & Why They're Useful

### **Data & Analytics APIs**

#### 1. **DexScreener API** (FREE)
- **What:** Real-time DEX (decentralized exchange) trading data
- **Why:** Discovers new token launches across BSC, Ethereum, Base, Polygon
- **What You Get:** Token pairs, prices, volume, liquidity, age
- **Limitations:** Limited historical OHLCV data on free tier
- **Docs:** https://docs.dexscreener.com/api/reference

#### 2. **GoPlus Security API** (FREE - 30 calls/minute, no auth required!)
- **What:** Automated smart contract security analysis
- **Why:** Detects rugpulls, honeypots, malicious code before you lose money
- **What You Get:** Contract verification, owner privileges, liquidity locks, holder distribution
- **Rate Limit:** 30 calls/min = 43,200/day (no API key needed!)
- **Key Use:** First-line defense against scams
- **Auth:** None required for free tier (`access_token=None`)
- **Higher Limits:** Contact service@gopluslabs.io for access token if >30 calls/min needed
- **Docs:** https://docs.gopluslabs.io/

#### 3. **Moralis Web3 API** (FREE - 40K compute units/day)
- **What:** Blockchain data aggregation across 30+ chains
- **Why:** Gets token metadata, holder lists, transfer history
- **What You Get:** Token balances, transaction history, wallet analytics
- **Key Use:** Analyze whale wallets and holder behavior
- **Docs:** https://docs.moralis.com/web3-data-api/evm

#### 4. **Alchemy RPC** (FREE - 100M compute units/month)
- **What:** Blockchain node infrastructure (connects to BSC network)
- **Why:** Required to read/write to blockchain (like an API for the blockchain itself)
- **What You Get:** Fast, reliable connection to BSC without running your own node
- **Alternative:** Infura (100K requests/day free)
- **Docs:** https://docs.alchemy.com/

#### 5. **CoinGecko API** (FREE Demo Plan - 30 calls/min)
- **What:** Cryptocurrency market data aggregator
- **Why:** Historical price data, market cap tracking
- **Limitations:** Advanced historical data requires $129/month Analyst tier
- **Key Use:** Limited backtesting data for established tokens
- **Docs:** https://docs.coingecko.com/

### **Python Libraries & Frameworks**

#### 1. **web3.py**
- **What:** Python library to interact with Ethereum-compatible blockchains (BSC, Polygon, Base)
- **Why:** Required to read smart contracts and execute DEX trades
- **What You Get:** Call PancakeSwap contracts, check balances, simulate swaps
- **Install:** `pip install web3`
- **Docs:** https://web3py.readthedocs.io/

#### 2. **backtesting.py**
- **What:** Lightweight Python framework for strategy backtesting
- **Why:** Test your trading logic on historical data before risking money
- **What You Get:** Performance metrics (win rate, Sharpe ratio, max drawdown), interactive charts
- **Install:** `pip install backtesting`
- **Docs:** https://kernc.github.io/backtesting.py/

#### 3. **pandas & numpy**
- **What:** Data manipulation and numerical computing libraries
- **Why:** Process token data, calculate indicators, analyze performance
- **What You Get:** DataFrames for time-series data, statistical functions
- **Install:** `pip install pandas numpy`

#### 4. **requests**
- **What:** HTTP library for API calls
- **Why:** Fetch data from DexScreener, GoPlus, Moralis, CoinGecko
- **Install:** `pip install requests`

#### 5. **python-telegram-bot**
- **What:** Interface to Telegram Bot API
- **Why:** Send yourself alerts when tokens match criteria or trades execute
- **Install:** `pip install python-telegram-bot`
- **Docs:** https://python-telegram-bot.readthedocs.io/

#### 6. **psycopg2** (PostgreSQL adapter)
- **What:** Python database connector for PostgreSQL
- **Why:** Store historical token data, track performance, persist state
- **Install:** `pip install psycopg2-binary`

### **Cloud Hosting Options**

#### 1. **DigitalOcean Droplet** (£4/month) ⭐ RECOMMENDED
- **What:** Linux VPS (Virtual Private Server)
- **Why:** Cheapest always-on option, simple setup, 512MB RAM sufficient
- **Specs:** 1 vCPU, 512MB RAM, 10GB SSD, 500GB bandwidth
- **Key Use:** Run Python bot 24/7 using `screen` or `tmux`
- **Signup:** https://www.digitalocean.com/

#### 2. **AWS EC2 t2.micro** (FREE for 12 months, then £7/month)
- **What:** Amazon cloud compute instance
- **Why:** Free tier perfect for testing, then affordable
- **Specs:** 1 vCPU, 1GB RAM (better than DigitalOcean for same eventual cost)
- **Limitation:** Free tier ends after 12 months or July 15, 2025 (whichever comes first)
- **Signup:** https://aws.amazon.com/free/

#### 3. **Render.com** (NOT RECOMMENDED for 24/7)
- **What:** Platform-as-a-Service (PaaS)
- **Why:** Easy deployment, but sleeps after 15 minutes on free tier
- **Issue:** Not suitable for continuous monitoring
- **Use Case:** Only if you manually trigger scans on-demand

### **Data Sources for Backtesting**

#### 1. **CryptoDataDownload** (FREE)
- **What:** Historical OHLCV CSV files for major exchanges
- **Why:** Clean, standardized data for backtesting
- **Limitation:** Only covers established tokens, not new launches
- **URL:** https://www.cryptodatadownload.com/

#### 2. **DexScreener Historical** (Limited)
- **What:** Some historical data via API
- **Why:** Recent tokens (7-90 days old)
- **Issue:** No deep historical OHLCV for free

#### 3. **Prospective Collection** (DIY)
- **What:** You scrape and store data starting NOW
- **Why:** Build your own dataset of new token launches over time
- **Benefit:** No survivorship bias, real-world conditions

---

## 📖 Key Trading Concepts Explained (For Beginners)

### **Market Cap (Market Capitalization)**
- **What:** Total value of all tokens in circulation
- **Formula:** Token Price × Circulating Supply
- **Example:** 1 million tokens @ $2 each = $2M market cap
- **Why It Matters:** Small caps ($500K-$5M) have more room to grow (10x possible) but higher risk

### **Liquidity**
- **What:** How easily you can buy/sell without moving the price
- **Where:** Locked in DEX pools (e.g., PancakeSwap USDT/TOKEN pair)
- **Example:** Token with $50K liquidity - a $5K buy might move price 5-10%
- **Why It Matters:** Low liquidity = high slippage (you pay more than expected)

### **Slippage**
- **What:** Difference between expected price and actual execution price
- **Cause:** Your trade moves the market (especially in low liquidity)
- **Example:** You want to buy at $1.00, but actually pay $1.05 (5% slippage)
- **Protection:** Set max slippage tolerance (e.g., 3%) - trade fails if exceeded

### **DEX (Decentralized Exchange)**
- **What:** Peer-to-peer trading using smart contracts (no central authority)
- **Examples:** PancakeSwap (BSC), Uniswap (Ethereum), QuickSwap (Polygon)
- **How:** Automated Market Maker (AMM) pools, not order books
- **Why BSC:** Much lower gas fees than Ethereum ($0.10 vs $10)

### **Smart Contract**
- **What:** Code running on blockchain that handles token logic
- **Functions:** Transfer, approve, swap, burn, mint
- **Risk:** Malicious code can steal your funds or prevent selling (honeypot)
- **Security:** GoPlus API analyzes contract for known scam patterns

### **Rugpull**
- **What:** Developers drain liquidity pool and disappear
- **Red Flags:** Unlocked liquidity, dev owns >50% supply, no contract verification
- **Prevention:** Check liquidity lock duration, analyze holder distribution

### **Liquidity Lock**
- **What:** Developers lock DEX pool tokens for X days/months
- **Why:** Proves they can't remove liquidity (rugpull prevention)
- **Good:** 6+ months lock
- **Red Flag:** No lock or <30 days

### **Holder Distribution**
- **What:** How tokens are spread across wallets
- **Metric:** Gini coefficient (0 = perfectly equal, 1 = one person owns everything)
- **Red Flag:** Top 10 wallets own >70% (pump & dump risk)
- **Healthy:** Distributed across 500+ holders, no single whale >20%

### **Volume/Liquidity Ratio**
- **What:** Daily trading volume ÷ Liquidity pool size
- **Wash Trading:** Fake volume (bots trading with themselves to look popular)
- **Red Flag:** Volume 10x+ liquidity = likely fake
- **Healthy:** Volume 0.5x - 3x liquidity

### **Gas Fees**
- **What:** Cost to execute transactions on blockchain
- **Paid In:** Network's native token (BNB on BSC, ETH on Ethereum)
- **BSC:** ~$0.10-0.30 per swap
- **Ethereum:** ~$5-50 per swap (why we avoid it for small trades)

### **Paper Trading**
- **What:** Simulated trading with fake money
- **Why:** Test your strategy risk-free before using real capital
- **How:** Bot tracks what WOULD happen if you made trades
- **Duration:** 2-6 months to validate edge

### **Backtesting**
- **What:** Testing strategy on historical data
- **Why:** See how rules would have performed in the past
- **Warning:** Past performance ≠ future results (especially with survivorship bias)
- **Use:** Eliminate obviously bad strategies, refine parameters

### **Expected Value (EV)**
- **What:** Average profit/loss per trade over many trades
- **Formula:** (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
- **Example:** 32% win rate, +240% avg win, 68% loss rate, -80% avg loss
  - EV = (0.32 × 240%) - (0.68 × 80%) = +42.4%
- **Why It Matters:** Positive EV = profitable long-term (if backtest is accurate)

### **Sharpe Ratio**
- **What:** Risk-adjusted return (higher is better)
- **Formula:** (Returns - Risk-Free Rate) / Volatility
- **Rule of Thumb:**
  - <1 = poor
  - 1-2 = good
  - >2 = excellent
- **Why It Matters:** Would you rather make 50% with wild swings or 30% smoothly?

### **Maximum Drawdown**
- **What:** Largest peak-to-trough decline in portfolio value
- **Example:** You grow £1000 → £2000, then drop to £1200
  - Max drawdown = (£2000 - £1200) / £2000 = 40%
- **Why It Matters:** Can you mentally handle losing 40% before recovering?

---

## 🗂️ Project Structure

```
super-pancake/
├── README.md                 # Project overview
├── PROJECT_PLAN.md          # This file
├── TASK_LIST.md             # Detailed implementation checklist
├── requirements.txt          # Python dependencies
├── config/
│   ├── settings.py          # API keys, chain configs
│   └── constants.py         # Market cap ranges, filters
├── src/
│   ├── discovery/
│   │   ├── dexscreener.py   # Fetch new tokens
│   │   ├── security.py      # GoPlus security checks
│   │   └── filters.py       # Age, market cap, liquidity filters
│   ├── analysis/
│   │   ├── holders.py       # Distribution analysis (Gini)
│   │   ├── volume.py        # Wash trading detection
│   │   └── scoring.py       # Composite quality score
│   ├── trading/
│   │   ├── paper_trader.py  # Simulated trading engine
│   │   ├── dex_interface.py # PancakeSwap integration (web3)
│   │   └── risk_mgmt.py     # Position sizing, stop loss
│   ├── backtest/
│   │   ├── engine.py        # Backtesting.py wrapper
│   │   ├── strategies.py    # Trading strategies
│   │   └── data_loader.py   # CSV/API historical data
│   ├── database/
│   │   ├── models.py        # PostgreSQL schema
│   │   └── queries.py       # Data access layer
│   └── utils/
│       ├── alerts.py        # Telegram notifications
│       └── logger.py        # Logging setup
├── tests/
│   └── ...                  # Unit tests
├── data/
│   ├── historical/          # Backtesting CSV files
│   └── cache/               # API response caching
└── scripts/
    ├── collect_data.py      # Daily token scraper
    ├── run_backtest.py      # Run historical analysis
    └── deploy.sh            # VPS deployment script
```

---

## 🚀 Implementation Phases

### **Phase 1: Foundation (Week 1-2)**
**Goal:** Set up development environment and core data pipeline

**Deliverables:**
- Python project structure
- API integrations (DexScreener, GoPlus, Moralis)
- PostgreSQL database for token storage
- Basic token discovery script (7-30 day filter)

### **Phase 2: Security Screening (Week 2-3)**
**Goal:** Implement automated safety checks

**Deliverables:**
- GoPlus contract analysis
- Holder distribution calculator (Gini coefficient)
- Volume/liquidity ratio checker
- Composite quality scoring system

### **Phase 3: Backtesting Engine (Week 3-4)**
**Goal:** Test strategies on historical data

**Deliverables:**
- Backtesting.py integration
- CSV data loader (CryptoDataDownload)
- Basic strategy: Buy 7-day tokens, hold 30 days
- Performance metrics dashboard (win rate, EV, Sharpe)

### **Phase 4: Paper Trading (Week 4-5)**
**Goal:** Simulate real trades on BSC

**Deliverables:**
- Web3.py PancakeSwap integration
- Paper trading engine (virtual wallet)
- Slippage/fee modeling
- Real-time P&L tracking

### **Phase 5: Cloud Deployment (Week 5-6)**
**Goal:** Run 24/7 on VPS

**Deliverables:**
- DigitalOcean droplet setup
- Cron jobs for hourly token scanning
- Telegram alert bot
- Monitoring dashboard (Flask/Streamlit)

### **Phase 6: Validation (Week 6-18)**
**Goal:** Run paper trading for 2-6 months

**Deliverables:**
- Track 100+ tokens prospectively
- Refine screening criteria based on outcomes
- Calculate actual win rate, EV, Sharpe ratio
- Decision point: Deploy real capital or pivot

---

## ⚠️ Realistic Expectations

### **What Will Definitely Work:**
- ✅ Building the tool (all tech is proven)
- ✅ Paper trading on BSC with £10 trades
- ✅ Learning web3 development and market dynamics
- ✅ Collecting prospective data starting now

### **What Probably Won't Work (Initially):**
- ❌ Backtesting 1000 tokens (data access limited on free tier)
- ❌ Achieving +42% EV immediately (backtest is biased/incomplete)
- ❌ £10 trades being representative (slippage hurts small size)
- ❌ First strategy iteration being profitable

### **What's Uncertain:**
- 🔶 Whether your screening criteria actually predict success
- 🔶 If 2024 patterns hold in 2025-2026 (market regime risk)
- 🔶 Competing with MEV bots and professional snipers
- 🔶 Finding tokens with enough liquidity for smooth execution

### **Success Probability Estimates:**
- **80% chance:** You build a working tool and learn a ton
- **40% chance:** Screening shows SOME predictive value
- **20% chance:** You find a small but real edge (5-15% annual return)
- **5% chance:** You achieve +42% EV from initial backtest
- **1% chance:** This becomes serious income

---

## 💰 Budget

### **Development Phase (Months 1-2):**
- **Hosting:** £0 (local development)
- **APIs:** £0 (all free tiers)
- **Trading:** £0 (paper trading only)
- **Total:** £0/month

### **Testing Phase (Months 3-6):**
- **VPS:** £4/month (DigitalOcean) or £0 (AWS free tier)
- **APIs:** £0 (stay within free limits)
- **Trading:** £0 (still paper trading)
- **Total:** £0-4/month

### **Small Capital Test (Month 7+):**
- **VPS:** £4-7/month
- **APIs:** £0-50/month (may need paid tier for higher volume)
- **Trading:** £500-1000 initial bankroll (expect to lose while learning)
- **Total:** £4-57/month + trading losses

---

## 📊 Key Performance Indicators (KPIs)

### **During Paper Trading:**
1. **Discovery Rate:** How many 7-30 day tokens pass filters per week?
   - Target: 5-20 tokens/week

2. **Rugpull Avoidance:** What % of tokens you DIDN'T buy got rugged?
   - Target: >80% (proves filters work)

3. **Win Rate:** % of paper trades that profit
   - Target: >30% (matches backtest)

4. **Average Winner:** Mean % gain on winning trades
   - Target: >100% (2x or better)

5. **Expected Value:** (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
   - Target: >20% (sustainably profitable)

6. **Sharpe Ratio:** Risk-adjusted returns
   - Target: >1.0 (decent), >1.5 (good)

### **Leading Indicators (Week 1-4):**
- Can you successfully call DexScreener API? (binary: yes/no)
- Does GoPlus catch known rugpulls in test cases? (accuracy %)
- Can you execute test swap on BSC testnet? (binary: yes/no)

---

## 🛡️ Risk Management Rules

### **Capital Allocation:**
- Max 2% of bankroll per trade (£20 if £1000 bankroll)
- Max 20% total exposure (10 positions max)
- Never add to losing positions

### **Entry Rules:**
- Token age: 7-30 days ✅
- Market cap: $500K - $5M ✅
- Liquidity: >$50K locked for >6 months ✅
- GoPlus security score: >70/100 ✅
- Gini coefficient: <0.7 (not too concentrated) ✅
- Volume/liquidity ratio: 0.5x - 3x (no wash trading) ✅

### **Exit Rules:**
- Stop loss: -50% from entry (cut losers fast)
- Take profit tier 1: +100% (sell 50% of position)
- Take profit tier 2: +300% (sell another 25%)
- Trailing stop: Let 25% run with 30% trailing stop

### **Circuit Breakers:**
- Pause all trading if:
  - 3 consecutive losses
  - Portfolio down >10% in one day
  - Liquidity on target token drops >50%
  - GoPlus API shows new security risk

---

## 📚 Learning Resources

### **Web3 & Smart Contracts:**
- [Web3.py Tutorial - PancakeSwap Swaps](https://www.publish0x.com/web3dev/web3py-walkthrough-to-swap-tokens-on-uniswap-pancakeswap-ape-xqmpllz)
- [BSC Developer Docs](https://docs.bnbchain.org/)

### **Trading & Backtesting:**
- [Backtesting.py Documentation](https://kernc.github.io/backtesting.py/)
- [QuantStart - Backtesting Strategies](https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks/)

### **Crypto Security:**
- [GoPlus Security Docs](https://docs.gopluslabs.io/)
- [Common DeFi Scams](https://academy.binance.com/en/articles/common-scams-on-mobile-devices)

### **Financial Concepts:**
- [Sharpe Ratio Explained](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Expected Value in Trading](https://www.investopedia.com/terms/e/expected-value.asp)
- [Gini Coefficient](https://www.investopedia.com/terms/g/gini-index.asp)

---

## 🎯 Next Steps

1. **Read through TASK_LIST.md** for detailed implementation checklist
2. **Set up API keys** (DexScreener, GoPlus, Moralis, Alchemy)
3. **Start Phase 1** (Foundation) - get basic token discovery working
4. **Join communities:**
   - r/CryptoMoonShots (see what manual traders look for)
   - r/algotrading (learn from systematic traders)
   - BSC Telegram groups (understand market dynamics)

---

## ❓ Questions to Answer Through This Project

1. **Do security APIs actually predict rugpulls?** (GoPlus effectiveness)
2. **Is holder distribution predictive?** (Gini coefficient signal)
3. **Does the 7-30 day window still work in 2025?** (regime dependency)
4. **What's the optimal market cap range?** (may not be $500K-$5M)
5. **How much does slippage/MEV erode profits?** (execution costs)
6. **Can this be profitable at <£1000 bankroll?** (minimum viable capital)

**This is a LEARNING project first, a trading system second.**

**Your edge is curiosity, discipline, and iteration - not magic algorithms.**

Good luck! 🥞
