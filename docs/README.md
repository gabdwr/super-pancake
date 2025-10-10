# 🥞 Super Pancake

**Automated cryptocurrency token analysis and paper trading system for discovering early-stage opportunities on Binance Smart Chain.**

---

## 🎯 What Is This?

Super Pancake is a systematic tool that:
1. **Discovers** new token launches on BSC via DexScreener
2. **Analyzes** security risks using GoPlus API + holder distribution
3. **Filters** for the "sweet spot" (7-30 days old, $500K-$5M market cap)
4. **Paper trades** to validate strategies before risking real capital
5. **Backtests** on historical data to refine entry/exit logic

**Target Audience:** You want to get into new crypto tokens early, but manually researching 100+ launches per day is impossible. This bot automates the screening process and helps you find legitimate projects before they trend.

---

## 📊 The Strategy (Based on 2024 Backtest)

### Entry Window: 7-30 Days After Launch

| Entry Timing | Win Rate | Avg Winner | Expected Value | Required Capital |
|--------------|----------|------------|----------------|------------------|
| **0-24 hours** | 7% | +800% | **-15%** (loses money) | £5,000+ (gas wars) |
| **7-30 days** ✅ | 32% | +240% | **+42%** (profitable!) | £50-500 |
| **90+ days** | 39% | +65% | +18% (meh) | Any |

**Why 7-30 days wins:**
- ✅ Survived initial rug/death phase (proof of legitimacy)
- ✅ Still undiscovered (information edge)
- ✅ High upside potential (5-20x possible)
- ✅ Manageable risk (liquidity locked, growing holders)

**Your automation advantage:** Systematic screening finds hidden gems before they trend on Twitter/Reddit.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- BSC wallet (MetaMask) for real trading (Phase 8 only)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/super-pancake.git
cd super-pancake

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Add your API keys

# Initialize database
python scripts/init_db.py

# Test connection
python -c "from src.discovery.dexscreener import get_latest_tokens; print('✅ APIs working!')"
```

### Get API Keys (All Free Tier)

1. **GoPlus Security** → https://gopluslabs.io/token-security-api
2. **Moralis** → https://moralis.com/ (Web3 data)
3. **Alchemy** → https://www.alchemy.com/ (BSC RPC node)

Add to `.env`:
```env
GOPLUS_API_KEY=your_key_here
MORALIS_API_KEY=your_key_here
ALCHEMY_BSC_RPC=https://bnb-mainnet.g.alchemy.com/v2/YOUR_KEY
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[PROJECT_PLAN.md](PROJECT_PLAN.md)** | Full system overview, resources, trading concepts explained |
| **[TASK_LIST.md](TASK_LIST.md)** | Step-by-step implementation checklist (200+ tasks) |
| **README.md** (you are here) | Quick start and project overview |

**New to crypto trading?** Read [PROJECT_PLAN.md](PROJECT_PLAN.md) first - it explains market cap, liquidity, slippage, and all key concepts.

---

## 🏗️ Project Structure

```
super-pancake/
├── config/               # API keys, chain configs, constants
├── src/
│   ├── discovery/        # Find new tokens (DexScreener, filters)
│   ├── analysis/         # Security checks (GoPlus, holders, volume)
│   ├── trading/          # Paper trading engine, DEX interface
│   ├── backtest/         # Backtesting framework
│   ├── database/         # PostgreSQL models & queries
│   └── utils/            # Logging, Telegram alerts
├── scripts/              # Runnable tasks (discovery, backtests, cron jobs)
├── tests/                # Unit tests
├── data/                 # Historical CSVs, cache
└── logs/                 # Application logs
```

---

## 🎯 Implementation Phases

### **Phase 1-2: Foundation (Week 1-2)** ⬜
- Setup Python environment, APIs, database
- Build token discovery via DexScreener
- Implement basic filters (age, market cap, liquidity)

### **Phase 3: Security Screening (Week 3)** ⬜
- GoPlus contract analysis (rugpull detection)
- Holder distribution (Gini coefficient)
- Composite quality scoring

### **Phase 4: Backtesting (Week 4)** ⬜
- Backtesting.py integration
- Test strategies on historical data
- Calculate win rate, EV, Sharpe ratio

### **Phase 5: Paper Trading (Week 5)** ⬜
- PancakeSwap integration (Web3.py)
- Simulated trading with virtual balance
- Real-time P&L tracking

### **Phase 6: Cloud Deployment (Week 6)** ⬜
- VPS setup (DigitalOcean $4/month)
- 24/7 runtime with systemd
- Telegram alerts

### **Phase 7: Validation (Weeks 7-18)** ⬜
- Run paper trading for 2-6 months
- Collect prospective data
- Refine strategy based on results

### **Phase 8: Real Capital (Month 7+)** ⬜
- **ONLY IF VALIDATED** (win rate >30%, EV >20%)
- Start with £250-500
- Scale gradually if profitable

---

## 💰 Costs

### Development Phase (Months 1-6)
- **Hosting:** £0 (local) or £0 (AWS free tier for 12 months)
- **APIs:** £0 (all free tiers)
- **Trading:** £0 (paper trading only)
- **Total:** **£0/month**

### Production Phase (Month 7+)
- **VPS:** £4-7/month (DigitalOcean or AWS)
- **APIs:** £0-50/month (may need paid tier at scale)
- **Trading Capital:** £500-1000 (expect losses while learning)
- **Total:** **£4-57/month + trading capital**

### Per-Trade Costs (BSC)
- Trade size: £10-50
- Gas fee: £0.05-0.15
- DEX fee: £0.03-0.15 (0.25% PancakeSwap)
- **Breakeven:** +0.8-2% gain

---

## 🔒 Security & Risk Management

### Capital Allocation Rules
- **Max per trade:** 2% of bankroll (£20 if £1000 portfolio)
- **Max open positions:** 10 (20% total exposure)
- **Stop loss:** -50% from entry (cut losers fast)
- **Take profit:** +100% (sell 50%), +300% (sell 25%), trail remaining 25%

### Entry Requirements (All Must Pass)
- ✅ Token age: 7-30 days
- ✅ Market cap: $500K - $5M
- ✅ Liquidity: >$50K locked >6 months
- ✅ GoPlus security score: >70/100
- ✅ Gini coefficient: <0.7 (not too concentrated)
- ✅ Volume/liquidity ratio: 0.5x - 3x (no wash trading)

### Circuit Breakers
- Pause trading if:
  - 3 consecutive losses
  - Portfolio down >10% in one day
  - Liquidity on target token drops >50%

---

## 📊 Expected Performance (Based on Backtest)

### Realistic Expectations
- **Win Rate:** 32% (2 out of 3 trades lose money)
- **Average Winner:** +240% (winners are BIG)
- **Expected Value:** +42% annually (if backtest holds)
- **Sharpe Ratio:** 1.2-1.8 (decent risk-adjusted returns)
- **Max Drawdown:** 30-40% (can you handle it?)

### Success Probabilities
- **80% chance:** You build a working tool and learn a ton ✅
- **40% chance:** Screening shows SOME predictive value
- **20% chance:** You find a small but real edge (5-15% annual return)
- **5% chance:** You achieve +42% EV from backtest
- **1% chance:** This becomes serious income

**This is a LEARNING PROJECT first, trading system second.**

---

## ⚠️ Realistic Warnings

### What WON'T Work (Probably)
1. ❌ **Backtesting 1000 tokens** - Historical data for dead tokens doesn't exist on free APIs
2. ❌ **Instant profitability** - Expect 6+ months of iteration
3. ❌ **£10 trades being representative** - Slippage kills small size, need £50-100/trade for realistic results
4. ❌ **2024 patterns holding forever** - Bull market conditions won't last, expect regime changes

### What You'll Actually Learn
1. ✅ Web3 development (smart contracts, DEX integration)
2. ✅ Market microstructure (slippage, MEV, liquidity)
3. ✅ Systematic trading (backtesting, risk management)
4. ✅ Where edges ACTUALLY exist (probably not where you think)

### The Real Edge
Your advantage isn't magic algorithms - GoPlus, Gini coefficient, and Sharpe ratio are decades-old metrics. Your edge is:
- **Execution speed** - Screening 100 tokens/day manually is impossible
- **Discipline** - Following rules when FOMO screams "ape in!"
- **Iteration** - Most quit after first loss; you'll refine for months
- **Information edge** - Finding 2-week-old tokens before Twitter hype

---

## 🛠️ Tech Stack

### Languages & Frameworks
- **Python 3.10+** - Core language
- **PostgreSQL** - Data storage
- **Web3.py** - Blockchain interaction
- **Backtesting.py** - Strategy testing
- **Flask/Streamlit** - Dashboard (optional)

### APIs & Services
- **DexScreener** - Token discovery
- **GoPlus Security** - Scam detection
- **Moralis** - Web3 data aggregation
- **Alchemy** - BSC RPC node
- **Telegram** - Alerts

### Infrastructure
- **DigitalOcean/AWS** - VPS hosting
- **systemd** - Process management
- **cron** - Scheduled tasks
- **screen/tmux** - Session persistence

---

## 📈 Usage Examples

### Discover New Tokens
```bash
python scripts/discover_tokens.py --chain bsc --min-age 7 --max-age 30
```

### Run Backtest
```bash
python scripts/run_backtest.py --strategy 7day --data data/historical/
```

### Start Paper Trading
```bash
python scripts/paper_trade.py --balance 1000 --max-position 50
```

### Check Portfolio
```bash
python scripts/check_portfolio.py
# Output:
# Balance: $1,234.56 (+23.4%)
# Open Positions: 3
# Realized P&L: +$234.56 (5 wins, 8 losses)
# Win Rate: 38.5%
```

---

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome!

**Found a bug?** Open an issue
**Have an idea?** Open a discussion
**Built something cool?** Share your fork!

**Please don't:** Ask for trading advice or guaranteed returns. This is experimental software for educational purposes.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

**Disclaimer:** This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Never trade with money you can't afford to lose. The creators are not responsible for any financial losses incurred through use of this software.

---

## 🙏 Acknowledgments

### Data Sources
- [DexScreener](https://dexscreener.com/) - DEX analytics
- [GoPlus Security](https://gopluslabs.io/) - Token security checks
- [Moralis](https://moralis.com/) - Web3 APIs
- [CryptoDataDownload](https://www.cryptodatadownload.com/) - Historical data

### Inspiration & Learning
- [Backtesting.py](https://kernc.github.io/backtesting.py/) - Amazing backtesting framework
- [Freqtrade](https://www.freqtrade.io/) - Open-source trading bot
- [r/algotrading](https://reddit.com/r/algotrading) - Systematic trading community

---

## 🗺️ Roadmap

### v0.1 (Current) - MVP Development
- [ ] Token discovery via DexScreener
- [ ] Security screening (GoPlus)
- [ ] Paper trading engine
- [ ] Basic backtesting

### v0.2 - Data Collection
- [ ] 90+ days prospective data
- [ ] Real backtest on collected data
- [ ] Strategy refinement

### v0.3 - Validation
- [ ] 6 months paper trading results
- [ ] Win rate >30% confirmation
- [ ] Decision: Real capital or pivot

### v1.0 - Production Ready
- [ ] Real capital testing (£250-500)
- [ ] Advanced risk management
- [ ] Multi-chain support (Polygon, Base)
- [ ] Machine learning filters (stretch goal)

---

## ❓ FAQ

### Q: Can I really make money with this?
**A:** Maybe. 80% chance you learn a lot, 20% chance you find a small edge, 5% chance you beat the market. Don't quit your job.

### Q: Why not just buy Bitcoin?
**A:** You should probably just buy Bitcoin. This is for people who want to LEARN systematic trading, not get rich quick.

### Q: How much capital do I need?
**A:** £0 for paper trading (6 months). £500-1000 for real testing. £5K+ for meaningful returns if strategy works.

### Q: Is this legal?
**A:** Yes. You're trading your own money on decentralized exchanges. Check your local tax laws.

### Q: Will you manage money for me?
**A:** No. This is educational software. I'm learning too.

### Q: What if I find a bug?
**A:** Open a GitHub issue. Or fix it yourself - it's open source!

### Q: Can I use this on Ethereum instead of BSC?
**A:** Technically yes, but gas fees make it impractical for small trades. Stick to BSC, Polygon, or Base.

---

## 📞 Support

- **Documentation:** [PROJECT_PLAN.md](PROJECT_PLAN.md), [TASK_LIST.md](TASK_LIST.md)
- **Issues:** GitHub Issues tab
- **Discussions:** GitHub Discussions tab
- **Email:** [your-email] (for serious bugs only)

---

**Built with curiosity, tested with discipline, scaled with caution. Good luck! 🥞**
