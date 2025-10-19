# Super Pancake - Data Analysis Guide

Comprehensive guide for analyzing token filter performance, price outcomes, and legitimacy detection.

---

## 📊 What Can You Analyze?

### 1. **Filter Transitions**
- Which tokens went from PASS → FAIL? (Rug pulls)
- Which tokens went from FAIL → PASS? (Recoveries)
- How long do tokens stay PASS before failing?
- Most common failure reasons

### 2. **Price Performance**
- ROI for PASS vs FAIL tokens
- Win rate: % of PASS tokens that are profitable
- Moonshots: How many tokens 2x, 5x, 10x?
- Average/median returns

### 3. **Legitimacy Detection**
- Classify tokens: Real Project vs Meme vs Scam
- Track liquidity growth (real projects grow, scams dump)
- Monitor holder growth (organic vs pump-and-dump)
- Analyze buy/sell pressure

### 4. **Filter Effectiveness**
- Precision: When we say PASS, how often is it profitable?
- Recall: What % of profitable tokens do we catch?
- Which individual filters matter most?
- False positive rate

### 5. **Rug Pull Detection**
- Detect liquidity drains
- Monitor LP unlock events
- Track whale accumulation
- Identify honeypot patterns

---

## 🚀 Quick Start

### Option 1: Python Analysis Script (Recommended)

**Install dependencies:**
```bash
pip install -r analysis/requirements.txt
```

**Run full analysis:**
```bash
python analysis/token_performance_analysis.py
```

**Output:**
- Console reports with statistics
- CSV exports of all data (`analysis/output/`)
- Visualization charts (ROI distribution, etc.)

---

### Option 2: SQL Queries (Manual)

**1. Open Supabase SQL Editor**
- Go to your Supabase project
- Navigate to SQL Editor

**2. Choose a query file:**
- `docs/analysis_queries.sql` - Comprehensive analysis queries
- `docs/dashboard_queries.sql` - Quick daily monitoring queries

**3. Copy/paste queries**
- Each query is documented with comments
- Run individual queries to get insights

---

## 📁 File Structure

```
super-pancake/
├── analysis/
│   ├── token_performance_analysis.py   # Main Python analysis script
│   ├── requirements.txt                 # Python dependencies
│   └── output/                          # Generated reports & charts
│
├── docs/
│   ├── analysis_queries.sql             # Comprehensive SQL queries
│   └── dashboard_queries.sql            # Quick reference queries
│
└── README_ANALYSIS.md                   # This file
```

---

## 🔍 Key Queries Explained

### Daily Monitoring Queries (dashboard_queries.sql)

| Query | Purpose | Use Case |
|-------|---------|----------|
| **Q1: Top performers (24h)** | Find biggest gainers | Daily opportunities |
| **Q2: PASS→FAIL transitions** | Detect rug pulls | Risk alerts |
| **Q3: First-time passes (today)** | New opportunities | Entry signals |
| **Q4: Strong buy pressure** | Bullish momentum | Trade confirmation |
| **Q5: Liquidity drains** | Rug pull alerts | Exit signals |
| **Q6-Q8: Summary stats** | Performance overview | Daily review |
| **Q9: Sustained growth** | Watchlist candidates | Long-term holds |
| **Q10: Recoveries** | FAIL→PASS tokens | Second chances |
| **Q11-Q12: Health check** | Data collection status | System monitoring |

### Comprehensive Analysis (analysis_queries.sql)

| Section | What It Shows | Why It Matters |
|---------|---------------|----------------|
| **1. Filter Transitions** | PASS→FAIL and FAIL→PASS | Understand filter stability |
| **2. Price Performance** | ROI, win rates, moonshots | Validate filter effectiveness |
| **3. Legitimacy Detection** | Real vs Meme vs Scam | Avoid pump-and-dumps |
| **4. Filter Effectiveness** | Precision, recall metrics | Tune filter thresholds |
| **5. Rug Pull Detection** | Liquidity drains, LP unlocks | Early warning system |

---

## 📈 Example Insights

### Filter Transition Analysis
```
📉 Found 12 PASS→FAIL transitions
   Average time to failure: 8.3 hours
   Median time to failure: 6.5 hours

   Most common failure reasons:
      - liquidity_too_low: 8 times
      - lp_locked_too_low: 5 times
      - concentration_too_low: 3 times
```

**Interpretation:** Most tokens fail due to liquidity drops within 8 hours.

---

### Price Performance Analysis
```
💰 PASS Token Performance:
   Total tokens: 45
   Win rate: 68.9% (31/45 profitable)
   Average ROI: +127.3%
   Median ROI: +64.5%
   Best performer: +1,847.2%
   Worst performer: -78.4%

   Moonshots:
      2x+  : 18 tokens (40.0%)
      5x+  : 6 tokens (13.3%)
      10x+ : 2 tokens (4.4%)
```

**Interpretation:** Filters work well - 69% win rate, avg 127% returns. 4% hit 10x.

---

### Legitimacy Scoring
```
🔍 Token Classification:
   Real Project: 12 (15.4%)
   Meme/Speculative: 48 (61.5%)
   Likely Scam: 18 (23.1%)

🏆 Top Real Projects (by liquidity growth):
   0x1234...abcd : +340% liquidity, +1,245 holders
   0x5678...efgh : +280% liquidity, +892 holders
   0x9012...ijkl : +195% liquidity, +673 holders
```

**Interpretation:** Focus on the 15% of tokens classified as "Real Projects" for best risk/reward.

---

## 🎯 How to Use Insights

### Daily Workflow

**Morning (9am):**
1. Run **Q11** (health check) - verify data collection working
2. Run **Q3** (first-time passes today) - find new opportunities
3. Run **Q6** (today's summary) - understand filter activity

**Afternoon (2pm):**
4. Run **Q1** (top performers 24h) - check if morning picks are gaining
5. Run **Q4** (strong buy pressure) - find momentum plays

**Evening (8pm):**
6. Run **Q2** (PASS→FAIL transitions) - identify failing tokens
7. Run **Q5** (liquidity drains) - rug pull alerts
8. Run **Q9** (sustained growth) - update watchlist

**Weekly (Sunday):**
9. Run Python script: `python analysis/token_performance_analysis.py`
10. Review ROI distribution chart
11. Analyze filter effectiveness metrics
12. Tune filter thresholds if needed

---

### Tuning Filter Thresholds

If precision is too low (too many false positives):
- **Increase** thresholds: `liquidity_usd >= 75000` (was 50K)
- **Increase** concentration: `concentration_score >= 70` (was 60)
- **Add** new filters: `holder_growth_rate >= 5%`

If recall is too low (missing good tokens):
- **Decrease** thresholds: `liquidity_usd >= 30000`
- **Decrease** LP lock requirement: `lp_locked_percent >= 40%`
- **Remove** restrictive filters

---

## 🛠️ Advanced Usage

### Custom Analysis

**Find tokens similar to a winner:**
```sql
-- Replace 0xWINNER with address of a good token
WITH winner_profile AS (
    SELECT
        AVG(liquidity_usd) as target_liq,
        AVG(concentration_score) as target_conc,
        AVG(lp_locked_percent) as target_lp
    FROM time_series_data
    WHERE token_address = '0xWINNER'
)
SELECT token_address, liquidity_usd, concentration_score
FROM time_series_data
WHERE filter_status = 'PASS'
  AND liquidity_usd BETWEEN (SELECT target_liq * 0.8 FROM winner_profile)
                         AND (SELECT target_liq * 1.2 FROM winner_profile)
ORDER BY snapshot_at DESC
LIMIT 10;
```

**Track a specific token:**
```sql
-- Full history of token 0xTARGET
SELECT
    snapshot_at,
    filter_status,
    price_usd,
    liquidity_usd,
    holder_count,
    buys_24h,
    sells_24h
FROM time_series_data
WHERE token_address = '0xTARGET'
ORDER BY snapshot_at ASC;
```

---

### Export Data for Excel/Sheets

1. Run any query in Supabase SQL Editor
2. Click "Download CSV" button
3. Import to Excel/Google Sheets for custom charts

---

## 📊 Visualization Ideas

**Create these charts in Excel/Python:**
1. **ROI Distribution** - Histogram of PASS token returns
2. **Win Rate Over Time** - Track filter effectiveness daily
3. **Liquidity Trends** - Line chart of avg liquidity for PASS tokens
4. **Failure Reasons** - Pie chart of why tokens fail
5. **Holder Growth** - Compare Real vs Meme vs Scam tokens

---

## 🚨 Alert System

**Set up automated alerts (future enhancement):**
- Telegram alert when liquidity drops >30% in 1 hour
- Email alert when new token passes for first time
- Discord webhook for PASS→FAIL transitions
- Slack notification for 10x+ gainers

---

## 📚 Understanding Metrics

### Win Rate
**Definition:** % of PASS tokens that are profitable after N hours

**Good:** >60% win rate
**Excellent:** >75% win rate

### Precision
**Definition:** When we say PASS, how often is it actually profitable?

**Formula:** (Profitable PASS tokens) / (All PASS tokens)

**Good:** >65% precision
**Excellent:** >80% precision

### Recall
**Definition:** What % of all profitable tokens do we catch?

**Formula:** (Profitable PASS tokens) / (All profitable tokens)

**Good:** >50% recall
**Excellent:** >70% recall

### Legitimacy Score (0-10)
- **8-10:** Real Project (liquidity + holders growing)
- **5-7:** Meme/Speculative (mixed signals)
- **0-4:** Likely Scam (declining metrics)

---

## 🔧 Troubleshooting

**No data returned:**
- Check if SQL migrations are applied
- Verify datafetch script is running hourly
- Confirm `filter_status` column exists

**Python script fails:**
- Install dependencies: `pip install -r analysis/requirements.txt`
- Check `.env` file has correct Supabase credentials
- Verify database connection with `psql` command

**Queries timeout:**
- Add `LIMIT 100` to large queries
- Create indexes on frequently queried columns
- Use `EXPLAIN ANALYZE` to optimize slow queries

---

## 🎓 Next Steps

1. **Run first analysis:**
   ```bash
   python analysis/token_performance_analysis.py
   ```

2. **Review results:**
   - Check `analysis/output/` for CSV reports
   - Look at ROI distribution chart
   - Note win rate and precision

3. **Make decisions:**
   - Are filters too strict? (Low recall)
   - Are filters too loose? (Low precision)
   - Which tokens should go on watchlist?

4. **Tune and repeat:**
   - Adjust filter thresholds in `critical_filters.py`
   - Run for another 7 days
   - Compare results

---

## 💡 Pro Tips

- **Focus on 7-day performance:** Short enough for quick feedback, long enough for trends
- **Track "Real Projects" separately:** These deserve deeper research
- **Don't chase 10x tokens:** Focus on consistent 2-3x wins
- **Watch liquidity, not just price:** Price can pump, liquidity can't fake
- **Holder growth = organic interest:** Real projects attract new holders daily
- **Buy pressure >55% = bullish:** More buys than sells = healthy demand

---

## 📞 Need Help?

**Query not working?**
- Check column names match your schema
- Add `LIMIT 10` for testing
- Use `EXPLAIN ANALYZE` to debug

**Want custom analysis?**
- Modify queries in `analysis_queries.sql`
- Add new functions to `token_performance_analysis.py`
- Create dashboard in tools like Metabase, Grafana

---

**Happy analyzing! 🚀**
