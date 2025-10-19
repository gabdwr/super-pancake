# Configurable Strategy Guide

**NEW in v3:** All filter thresholds are now configurable via environment variables, keeping your exact strategy private!

---

## Why Make Filters Configurable?

### Before (v2):
- ❌ Filter thresholds hardcoded in `critical_filters.py`
- ❌ Strategy visible to anyone who reads the code
- ❌ Required code changes to tune filters
- ❌ All repos using this code had identical strategy

### After (v3):
- ✅ Filter thresholds in `.env` (not committed to git)
- ✅ Your exact strategy stays private
- ✅ Tune filters without touching code
- ✅ Each user can have unique competitive edge

---

## How It Works

### 1. Filter Configuration Lives in `.env`

Your `.env` file (which is **never committed** to git) contains your secret filter values:

```bash
# YOUR SECRET STRATEGY (in .env - NOT committed)
FILTER_MIN_LP_LOCKED=30
FILTER_MIN_CONCENTRATION=50
FILTER_MIN_LIQUIDITY_USD=20000
FILTER_MAX_BUY_TAX=10
FILTER_MAX_SELL_TAX=10
FILTER_ALLOW_HONEYPOT=False
FILTER_ALLOW_MINTABLE=False
```

### 2. Code Uses Environment Variables

The code in `critical_filters.py` reads these values:

```python
# critical_filters.py (PUBLIC in git)
FILTER_MIN_LP_LOCKED = float(os.getenv('FILTER_MIN_LP_LOCKED', '30.0'))
FILTER_MIN_CONCENTRATION = float(os.getenv('FILTER_MIN_CONCENTRATION', '50.0'))
# ... etc
```

### 3. GitHub Actions Uses Secrets

Your GitHub Actions workflows read from GitHub Secrets (configured at repo → Settings → Secrets):

```yaml
# .github/workflows/datafetch.yml (PUBLIC in git)
FILTER_MIN_LP_LOCKED=${{ secrets.FILTER_MIN_LP_LOCKED }}
FILTER_MIN_CONCENTRATION=${{ secrets.FILTER_MIN_CONCENTRATION }}
# ... etc
```

---

## Setup Guide

### Step 1: Configure Your Local `.env`

Your `.env` file already has the filter configuration added. Edit the values to match your strategy:

```bash
# Open your .env file
nano .env  # or use your editor

# Find the "CRITICAL FILTERS" section and adjust values:
FILTER_MIN_LP_LOCKED=30           # Your value here
FILTER_MIN_CONCENTRATION=50       # Your value here
FILTER_MIN_LIQUIDITY_USD=20000    # Your value here
FILTER_MAX_BUY_TAX=10             # Your value here
FILTER_MAX_SELL_TAX=10            # Your value here
```

### Step 2: Add Secrets to GitHub

Go to your repo settings and add these as **Repository Secrets**:

**URL:** https://github.com/gabdwr/super-pancake/settings/secrets/actions

Click "New repository secret" for each:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `FILTER_ALLOW_HONEYPOT` | `False` | `False` |
| `FILTER_MIN_LP_LOCKED` | Your min LP % | `30` |
| `FILTER_MIN_CONCENTRATION` | Your min concentration | `50` |
| `FILTER_MIN_LIQUIDITY_USD` | Your min liquidity | `20000` |
| `FILTER_MAX_BUY_TAX` | Your max buy tax | `10` |
| `FILTER_MAX_SELL_TAX` | Your max sell tax | `10` |
| `FILTER_ALLOW_MINTABLE` | `False` | `False` |

**Important:** Use the **same values** from your `.env` file!

### Step 3: Verify Configuration

Run locally to test:

```bash
# This will print your loaded configuration
python run_datafetch_and_filtration.py

# Look for output like:
# 🔧 Critical Filters Configuration:
#    Allow Honeypot: False
#    Min LP Locked: 30.0%
#    Min Concentration: 50.0
#    Min Liquidity: $20,000
#    Max Buy Tax: 10.0%
#    Max Sell Tax: 10.0%
#    Allow Mintable: False
```

---

## Filter Tuning Guide

### Understanding Each Filter

#### 1. `FILTER_ALLOW_HONEYPOT` (Default: `False`)

**What it does:** Rejects tokens identified as honeypots by GoPlus API

**Tuning:**
- `False` (recommended): Block all honeypots
- `True` (risky): Allow honeypots (not recommended!)

**When to change:** Never. Honeypots are untradeab le scams.

---

#### 2. `FILTER_MIN_LP_LOCKED` (Default: `30`)

**What it does:** Minimum % of LP tokens that must be locked

**Why it matters:**
- Low LP lock = dev can rug pull liquidity at any time
- High LP lock = liquidity is safe (locked in contract)

**Tuning:**
- **Conservative (60-100%):** Only very safe, established tokens
- **Balanced (30-60%):** Catches most legitimate new tokens
- **Aggressive (0-30%):** Catches earlier opportunities but higher rug risk

**Your current:** `30%` (balanced - catches new tokens with some protection)

**Recommendation:** Keep 30% unless you see too many rugs (then raise to 50%)

---

#### 3. `FILTER_MIN_CONCENTRATION` (Default: `50`)

**What it does:** Minimum liquidity concentration score (0-100)

**Why it matters:**
- Low score = liquidity fragmented across many pools (wash trading risk)
- High score = liquidity concentrated in main pool (more legitimate)

**Tuning:**
- **Conservative (70-100):** Only tokens with concentrated liquidity
- **Balanced (50-70):** Allows some fragmentation for new tokens
- **Aggressive (0-50):** Catches very early tokens but higher scam risk

**Your current:** `50` (balanced - allows new tokens with reasonable concentration)

**Recommendation:** Keep 50 unless analysis shows fragmented tokens underperform (then raise to 60)

---

#### 4. `FILTER_MIN_LIQUIDITY_USD` (Default: `20000`)

**What it does:** Minimum USD liquidity required

**Why it matters:**
- Low liquidity = high slippage, easy to manipulate, low volume
- High liquidity = safer, more established, harder to manipulate

**Tuning:**
- **Conservative ($50K+):** Only established tokens
- **Balanced ($10K-$50K):** Catches newer tokens with some liquidity
- **Aggressive ($1K-$10K):** Very early tokens, high risk

**Your current:** `$20K` (balanced - new tokens with meaningful liquidity)

**Trade-offs:**
- Lower → Catch mooners earlier, but higher scam rate
- Higher → Safer picks, but miss early pumps

**Recommendation:**
- Start with $20K
- If analysis shows low-liquidity tokens have good ROI, lower to $10K
- If too many scams, raise to $30K

---

#### 5. `FILTER_MAX_BUY_TAX` (Default: `10`)

**What it does:** Maximum % tax on buy transactions

**Why it matters:**
- High buy tax = less profit (you pay more to enter)
- Most legitimate tokens have 0-5% buy tax

**Tuning:**
- **Conservative (0-5%):** Only low-tax tokens
- **Balanced (5-10%):** Standard range for new tokens
- **Aggressive (10-20%):** Allow high-tax tokens (rare, risky)

**Your current:** `10%` (balanced - allows standard tax tokens)

**Recommendation:** Keep 10% unless you see most profitable tokens have <5% (then lower to 5%)

---

#### 6. `FILTER_MAX_SELL_TAX` (Default: `10`)

**What it does:** Maximum % tax on sell transactions

**Why it matters:**
- High sell tax = less profit when exiting
- Very high sell tax (>15%) can indicate honeypot

**Tuning:**
- **Conservative (0-5%):** Only low-tax exit
- **Balanced (5-10%):** Standard range
- **Aggressive (10-20%):** Allow high-tax tokens

**Your current:** `10%` (balanced)

**⚠️ Warning:** Sell tax >10% is often a scam indicator. Be very careful raising this.

**Recommendation:** Keep at 10%. If token has 15%+ sell tax, it's likely a honeypot.

---

#### 7. `FILTER_ALLOW_MINTABLE` (Default: `False`)

**What it does:** Rejects tokens where owner can mint new supply

**Why it matters:**
- Mintable = dev can inflate supply at will (dilute your holdings)
- Non-mintable = fixed supply (safer)

**Tuning:**
- `False` (recommended): Block mintable tokens
- `True` (risky): Allow mintable (not recommended)

**When to change:** Rarely. Mintable tokens are high risk.

---

## Strategy Presets

Here are some preset configurations for different risk profiles:

### 🛡️ Conservative (Low Risk, Low Reward)
```bash
FILTER_MIN_LP_LOCKED=60
FILTER_MIN_CONCENTRATION=70
FILTER_MIN_LIQUIDITY_USD=50000
FILTER_MAX_BUY_TAX=5
FILTER_MAX_SELL_TAX=5
FILTER_ALLOW_HONEYPOT=False
FILTER_ALLOW_MINTABLE=False
```
**Use when:** You want maximum safety, don't mind missing early pumps

---

### ⚖️ Balanced (Your Current Strategy)
```bash
FILTER_MIN_LP_LOCKED=30
FILTER_MIN_CONCENTRATION=50
FILTER_MIN_LIQUIDITY_USD=20000
FILTER_MAX_BUY_TAX=10
FILTER_MAX_SELL_TAX=10
FILTER_ALLOW_HONEYPOT=False
FILTER_ALLOW_MINTABLE=False
```
**Use when:** You want to catch newer tokens with reasonable safety

---

### 🚀 Aggressive (High Risk, High Reward)
```bash
FILTER_MIN_LP_LOCKED=10
FILTER_MIN_CONCENTRATION=30
FILTER_MIN_LIQUIDITY_USD=5000
FILTER_MAX_BUY_TAX=15
FILTER_MAX_SELL_TAX=12
FILTER_ALLOW_HONEYPOT=False
FILTER_ALLOW_MINTABLE=False
```
**Use when:** You want to catch tokens very early (expect more scams!)

---

## Backtesting Your Strategy

After collecting 7+ days of clean data, use the analysis script to optimize:

```bash
python analysis/token_performance_analysis.py
```

### Key Metrics to Watch:

1. **Win Rate** (target: 60-70%)
   - Too low? Tighten filters (raise LP lock, concentration, liquidity)
   - Too high but low recall? Loosen filters slightly

2. **Average ROI** (target: +50% to +100%)
   - Negative? Strategy is broken, tighten all filters
   - Low positive? Tighten filters for better selectivity

3. **Recall** (target: 40-50%)
   - Too low? Filters too strict, missing opportunities
   - Too high? Filters too loose, catching too many scams

### Iterative Tuning Process:

1. **Start with Balanced preset** (your current values)
2. **Collect 7 days of data**
3. **Run analysis** to see win rate, ROI, recall
4. **Adjust ONE filter at a time** based on failure reasons
5. **Wait another 3-7 days** for new data
6. **Re-analyze and compare** to previous period
7. **Repeat** until metrics hit targets

---

## What's Visible in Public Repo

When you make your repo public, people will see:

### ✅ Public (in git):
- The code that loads filter values from environment
- Default fallback values (30, 50, 20000, 10, 10)
- The filtering logic itself
- How concentration score is calculated

### 🔒 Private (NOT in git):
- Your actual filter thresholds (in `.env` and GitHub Secrets)
- Your exact strategy values
- How you've tuned based on backtesting
- Your competitive edge

### Example:

Someone cloning your public repo will see:
```python
# This is public - they see the DEFAULT values
FILTER_MIN_LP_LOCKED = float(os.getenv('FILTER_MIN_LP_LOCKED', '30.0'))
```

But they WON'T see:
```bash
# This is in YOUR .env - not committed - they don't see this!
FILTER_MIN_LP_LOCKED=42  # Your secret optimized value
```

---

## Security Checklist

Before making repo public, verify:

- [ ] `.env` file is listed in `.gitignore` ✅
- [ ] `.env` file is NOT tracked by git ✅
- [ ] All filter values are in `.env` (not hardcoded) ✅
- [ ] `.env.example` exists with placeholder values ✅
- [ ] GitHub Secrets are set for all `FILTER_*` variables
- [ ] Local testing shows correct values being loaded

---

## Quick Reference

### Current Filter Values (Balanced Strategy)

| Filter | Variable | Your Value | What It Does |
|--------|----------|------------|--------------|
| Honeypot | `FILTER_ALLOW_HONEYPOT` | `False` | Block honeypots |
| LP Lock | `FILTER_MIN_LP_LOCKED` | `30` | Min 30% LP locked |
| Concentration | `FILTER_MIN_CONCENTRATION` | `50` | Min score 50/100 |
| Liquidity | `FILTER_MIN_LIQUIDITY_USD` | `20000` | Min $20K liquidity |
| Buy Tax | `FILTER_MAX_BUY_TAX` | `10` | Max 10% buy tax |
| Sell Tax | `FILTER_MAX_SELL_TAX` | `10` | Max 10% sell tax |
| Mintable | `FILTER_ALLOW_MINTABLE` | `False` | Block mintable |

---

## Troubleshooting

### Filters not being applied correctly

**Check 1:** Verify `.env` file exists
```bash
ls -la .env
```

**Check 2:** Verify values are loaded (check logs)
```bash
python run_datafetch_and_filtration.py | grep "Critical Filters Configuration"
```

**Check 3:** Check for syntax errors in `.env`
```bash
# Values should NOT have quotes
FILTER_MIN_LP_LOCKED=30        # ✅ Correct
FILTER_MIN_LP_LOCKED="30"      # ❌ Wrong (will work but unnecessary)
FILTER_MIN_LP_LOCKED='30'      # ❌ Wrong
```

### GitHub Actions using wrong values

**Check:** Verify all secrets are set
1. Go to https://github.com/gabdwr/super-pancake/settings/secrets/actions
2. Ensure all 7 `FILTER_*` secrets exist
3. Values should match your `.env` file

---

## FAQ

**Q: Can I have different filters for different chains?**
A: Not currently, but you could add `FILTER_MIN_LP_LOCKED_BSC` vs `FILTER_MIN_LP_LOCKED_BASE` if needed.

**Q: What happens if I don't set a filter variable?**
A: Code uses the default fallback value (30, 50, 20000, 10, 10, etc.)

**Q: Can I change filters without restarting?**
A: No - filters are loaded when the module imports. Restart script to reload.

**Q: Should I commit `.env.example`?**
A: YES! `.env.example` is safe to commit (contains no real values)

**Q: Should I commit `.env`?**
A: NO! Never commit `.env` - it contains your actual secrets

---

**Next Steps:**

1. ✅ Make sure your `.env` has the filter values you want
2. ✅ Add those same values to GitHub Secrets
3. ✅ Make repo public (or keep private with configured filters)
4. ✅ Collect data for 7 days
5. ✅ Run analysis and tune filters
6. ✅ Iterate until you hit target win rate (60-70%)
