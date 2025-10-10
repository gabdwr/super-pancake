# Super Pancake Bot - Oracle Cloud Deployment Guide

Complete guide to deploy your token discovery bot on Oracle Cloud with automated 6-hour execution.

---

## Your VM Details

- **Public IP:** `145.241.221.24`
- **Username:** `opc`
- **SSH Key:** `~/Downloads/superpancakeoracle.key`
- **OS:** Oracle Linux (Python 3.9.21 installed)
- **VM Name:** `superduperPancakeVM`

---

## Quick Start (5 Steps)

### 1. Upload Your Code to the VM

From your **local machine**, run:

```bash
scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/
```

This copies your entire project folder to the VM.

### 2. SSH into the VM

```bash
ssh -i ~/Downloads/superpancakeoracle.key opc@145.241.221.24
```

### 3. Run the Deployment Script

```bash
cd ~/super-pancake
bash scripts/deploy_oracle.sh
```

This will:
- Install Python 3.11 and dependencies
- Create virtual environment
- Install all Python packages
- Create `.env` file (you'll need to add your API keys)
- Set up log directory

### 4. Configure Your API Keys

Edit the `.env` file and add your credentials:

```bash
nano ~/super-pancake/.env
```

**Required:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_number
```

**Optional (for enhanced features):**
```env
MORALIS_API_KEY=your_moralis_key
BSCSCAN_API_KEY=your_bscscan_key
```

Press `Ctrl+O` to save, `Enter` to confirm, `Ctrl+X` to exit.

### 5. Set Up Cron for Automated Execution

```bash
bash ~/super-pancake/scripts/setup_cron.sh
```

Choose option **1** for every 6 hours (recommended).

---

## Detailed Walkthrough

### Step-by-Step Deployment

#### 1. **Connect to VM**

```bash
ssh -i ~/Downloads/superpancakeoracle.key opc@145.241.221.24
```

You should see:
```
[opc@superduperPancakeVM ~]$
```

#### 2. **Upload Code (Two Methods)**

**Method A: SCP Upload (Recommended)**

From your **local machine** (open a new terminal, don't SSH yet):

```bash
# Upload entire project
scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/

# Verify upload
ssh -i ~/Downloads/superpancakeoracle.key opc@145.241.221.24 "ls -la ~/super-pancake"
```

**Method B: Git Clone**

If your code is on GitHub:

```bash
# On the VM
cd ~
git clone https://github.com/your-username/super-pancake.git
cd super-pancake
```

#### 3. **Run Deployment Script**

```bash
cd ~/super-pancake
bash scripts/deploy_oracle.sh
```

The script will:
1. ✅ Install Python 3.11, git, and development tools
2. ✅ Create virtual environment
3. ✅ Install Python dependencies (web3, requests, pandas, etc.)
4. ✅ Create `.env` template file
5. ✅ Create logs directory
6. ✅ Run a test (optional)

**During deployment:**
- When asked about cloning, choose **option 2** (files already uploaded)
- When prompted, **edit the `.env` file** to add your API keys

#### 4. **Configure Environment Variables**

The deployment script will create a `.env` file. Edit it:

```bash
nano ~/super-pancake/.env
```

**Minimum required configuration:**

```env
# Telegram Alerts (REQUIRED)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# API Keys (optional but recommended)
MORALIS_API_KEY=your_key_here
BSCSCAN_API_KEY=your_key_here
ALCHEMY_BSC_RPC=https://bsc-dataseed.binance.org/

# Trading Parameters
PAPER_TRADING=True
PAPER_TRADING_BALANCE=1000
MAX_POSITION_SIZE=50

# Token Filters
MIN_TOKEN_AGE_DAYS=7
MAX_TOKEN_AGE_DAYS=30
MIN_MARKET_CAP_USD=500000
MAX_MARKET_CAP_USD=5000000
MIN_LIQUIDITY_USD=10000
MIN_GOPLUS_SCORE=70
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

#### 5. **Test Manually First**

Before setting up cron, test the bot manually:

```bash
cd ~/super-pancake
source venv/bin/activate
python test_discovery_and_liquidity.py
```

You should see:
- Token discovery running
- Liquidity analysis for each token
- Telegram messages arriving on your phone

If this works, you're ready for automated execution!

#### 6. **Set Up Automated Execution (Cron)**

```bash
bash ~/super-pancake/scripts/setup_cron.sh
```

**Choose your schedule:**
- **Option 1:** Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC) - **Recommended**
- Option 2: Every 4 hours
- Option 3: Every hour
- Option 4: Every 12 hours
- Option 5: Custom

The script will:
1. Make the wrapper script executable
2. Configure crontab with your chosen schedule
3. Show you the next execution times
4. Optionally run a test

**Test the cron job:**

When asked "Do you want to run a test now?", choose **yes**.

This will execute the bot once and show you the output.

---

## Verification

### Check Cron is Configured

```bash
crontab -l
```

You should see:
```
# Super Pancake Token Discovery Bot
0 */6 * * * /home/opc/super-pancake/scripts/run_discovery_cron.sh >> /home/opc/super-pancake/logs/cron.log 2>&1
```

### View Logs

```bash
# View latest discovery log
ls -lt ~/super-pancake/logs/discovery_*.log | head -1 | xargs tail -f

# View cron log
tail -f ~/super-pancake/logs/cron.log

# View all recent logs
ls -lth ~/super-pancake/logs/
```

### Check Telegram Alerts

You should receive:
1. **Script Start** notification when bot begins
2. **Token Discovery** alerts for tokens with score ≥ 60
3. **Script Complete** summary when finished

---

## Monitoring & Maintenance

### Check if Bot is Running

```bash
# Check recent cron executions
grep "Super Pancake" ~/super-pancake/logs/cron.log | tail -20

# Check latest discovery log
ls -t ~/super-pancake/logs/discovery_*.log | head -1 | xargs cat
```

### View Real-Time Logs

```bash
# Watch cron log (shows when bot runs)
tail -f ~/super-pancake/logs/cron.log

# Watch latest discovery log (shows token analysis)
watch -n 2 'ls -t ~/super-pancake/logs/discovery_*.log | head -1 | xargs tail -20'
```

### Manual Execution

To run the bot manually anytime:

```bash
# Run with wrapper (logs to file)
bash ~/super-pancake/scripts/run_discovery_cron.sh

# Or run directly (output to console)
cd ~/super-pancake
source venv/bin/activate
python test_discovery_and_liquidity.py
```

### Update Code

When you update your local code:

```bash
# On your local machine
scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/

# Or on VM if using Git
ssh -i ~/Downloads/superpancakeoracle.key opc@145.241.221.24
cd ~/super-pancake
git pull
```

No need to reinstall dependencies unless requirements.txt changed.

### Modify Cron Schedule

```bash
# Edit crontab directly
crontab -e

# Or re-run setup script
bash ~/super-pancake/scripts/setup_cron.sh
```

### Stop Automated Execution

```bash
# Remove cron job
crontab -e
# Delete the line with "Super Pancake"

# Or remove all cron jobs
crontab -r
```

---

## Troubleshooting

### Bot Not Running

**Check cron is active:**
```bash
systemctl status crond
# If not running: sudo systemctl start crond
```

**Check cron errors:**
```bash
tail -50 ~/super-pancake/logs/cron.log
```

### No Telegram Alerts

**Verify credentials:**
```bash
grep TELEGRAM ~/super-pancake/.env
```

Should show your bot token and chat ID (not blank).

**Test manually:**
```bash
cd ~/super-pancake
source venv/bin/activate
python -m src.utils.telegram_alerts
```

### Python Errors

**Check virtual environment:**
```bash
ls ~/super-pancake/venv/bin/python
source ~/super-pancake/venv/bin/activate
python --version  # Should be 3.9 or 3.11
```

**Reinstall dependencies:**
```bash
cd ~/super-pancake
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Logs Not Created

**Check permissions:**
```bash
ls -la ~/super-pancake/logs/
mkdir -p ~/super-pancake/logs/
chmod 755 ~/super-pancake/logs/
```

### VM Can't Connect to Internet

**Test connectivity:**
```bash
ping -c 3 google.com
curl https://api.dexscreener.com/latest/dex/tokens/0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
```

**Check firewall (Oracle Cloud):**
- Go to Oracle Cloud Console
- Compute → Instances → Your VM
- Virtual Cloud Network → Security Lists
- Ensure **egress** (outbound) rules allow HTTPS (port 443)

---

## Useful Commands Reference

```bash
# Connect to VM
ssh -i ~/Downloads/superpancakeoracle.key opc@145.241.221.24

# Upload files from local machine
scp -i ~/Downloads/superpancakeoracle.key -r ~/Documents/super-pancake opc@145.241.221.24:~/

# Check VM resources
free -h         # Memory usage
df -h           # Disk usage
top             # CPU usage (press 'q' to quit)

# View crontab
crontab -l

# Edit crontab
crontab -e

# View logs
tail -f ~/super-pancake/logs/cron.log
ls -lth ~/super-pancake/logs/

# Activate virtual environment
cd ~/super-pancake
source venv/bin/activate

# Run bot manually
python test_discovery_and_liquidity.py

# Check Python packages
pip list

# Update code
git pull  # If using Git
# Or upload via SCP from local machine

# Restart cron daemon
sudo systemctl restart crond

# Check system time (for cron schedule)
date
timedatectl  # Shows timezone (should be UTC)
```

---

## Schedule Examples

The cron expression format: `minute hour day month weekday`

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 6 hours | `0 */6 * * *` | 00:00, 06:00, 12:00, 18:00 UTC |
| Every 4 hours | `0 */4 * * *` | Every 4 hours on the hour |
| Every hour | `0 * * * *` | Top of every hour |
| Every 12 hours | `0 */12 * * *` | 00:00, 12:00 UTC |
| Daily at 8 AM | `0 8 * * *` | Once per day |
| Twice daily | `0 8,20 * * *` | 08:00 and 20:00 UTC |
| Every 30 mins | `*/30 * * * *` | Every 30 minutes |

**Current setup:** Every 6 hours (recommended for token discovery)

---

## Cost Optimization

Your Oracle Cloud Free Tier includes:
- ✅ VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM) - **Always Free**
- ✅ 200 GB outbound data transfer/month - **Always Free**
- ✅ No time limit

**Your bot usage:**
- Runs 4 times/day (every 6 hours)
- ~5 minutes per run
- Minimal CPU/RAM/bandwidth

**Total cost:** $0.00/month ✅

---

## Security Best Practices

1. ✅ **Never commit `.env` to Git** - It's already in `.gitignore`
2. ✅ **Keep SSH key secure** - Don't share `superpancakeoracle.key`
3. ✅ **Use strong Telegram bot** - Only you should have the token
4. ✅ **Regular updates** - Keep system and packages updated:
   ```bash
   sudo dnf update -y
   ```
5. ✅ **Monitor logs** - Check for suspicious activity

---

## Next Steps

1. ✅ Bot is running automatically every 6 hours
2. ✅ Receiving Telegram alerts
3. 📊 Monitor for 7-14 days to see what tokens are discovered
4. 📈 Adjust filters in `.env` if needed (score thresholds, liquidity minimums, etc.)
5. 💰 After validation, consider implementing paper trading (Phase 5 in TASK_LIST.md)

---

## Support

- **Documentation:** [docs/TASK_LIST.md](TASK_LIST.md)
- **Telegram Setup:** [docs/TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
- **Project Plan:** [docs/PROJECT_PLAN.md](PROJECT_PLAN.md)

---

**Status:** 🥞 Your bot is now running 24/7 on Oracle Cloud! Check Telegram for alerts.

**Last Updated:** 2025-10-09
