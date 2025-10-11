# GitHub Actions Setup Guide

This guide explains how to set up automated cron jobs using GitHub Actions for your Super Pancake crypto bot.

## 📋 Overview

Two workflows run automatically:

1. **DexScreener Scraper** - Runs **every hour** to discover new tokens
2. **Token Metrics Fetcher** - Runs **once per day** to collect metrics for all tokens

## 🚀 Setup Steps

### Step 1: Push Code to GitHub

```bash
# If you haven't already initialized git:
git init
git add .
git commit -m "Add GitHub Actions workflows"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/super-pancake.git
git branch -M main
git push -u origin main
```

### Step 2: Add GitHub Secrets

GitHub Actions needs your environment variables as secrets.

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of these secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `SUPABASE_HOST` | Your Supabase database host | `db.zzthxokfkpqgjruaudid.supabase.co` |
| `SUPABASE_PORT` | Port number | `5432` |
| `SUPABASE_USERNAME` | Database username | `postgres` |
| `SUPABASE_PASSWORD` | Database password | `your_password_here` |
| `SUPABASE_DBNAME` | Database name | `postgres` |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `123456789` |

**Important:** Click "Add secret" for each one.

### Step 3: Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. You should see workflows ready to run
3. If asked, click **"I understand my workflows, go ahead and enable them"**

### Step 4: Test the Workflows

**Manual test (recommended before waiting for cron):**

1. Go to **Actions** tab
2. Click on **"DexScreener Hourly Scraper"** or **"Token Metrics Daily Fetch"**
3. Click **"Run workflow"** dropdown → **"Run workflow"** button
4. Watch the logs in real-time
5. Check your Telegram for success notification
6. Verify data in Supabase

### Step 5: Monitor Scheduled Runs

Once enabled, the workflows will run automatically:

- **DexScreener**: Every hour (e.g., 1:00, 2:00, 3:00 UTC)
- **DataFetch**: Every day at midnight UTC

**To view logs:**
1. Go to **Actions** tab
2. Click on a workflow run
3. Expand the job steps to see detailed logs

---

## 📅 Schedule Details

### DexScreener (Hourly)

```yaml
schedule:
  - cron: '0 * * * *'  # Every hour on the hour
```

**When it runs:**
- 00:00 UTC, 01:00 UTC, 02:00 UTC, ..., 23:00 UTC
- Approximately 24 runs per day
- May be delayed 1-5 minutes during GitHub's high load

### DataFetch (Daily)

```yaml
schedule:
  - cron: '0 0 * * *'  # Midnight UTC daily
```

**When it runs:**
- 00:00 UTC every day (midnight)
- To change time, edit `datafetch.yml`:
  - `0 12 * * *` = Noon UTC
  - `0 6 * * *` = 6 AM UTC
  - `0 */6 * * *` = Every 6 hours

---

## 🔧 Customization

### Change Schedule

Edit `.github/workflows/dexscraper.yml` or `.github/workflows/datafetch.yml`:

```yaml
schedule:
  - cron: 'MINUTE HOUR DAY MONTH WEEKDAY'
```

**Examples:**
```yaml
'0 * * * *'       # Every hour
'*/30 * * * *'    # Every 30 minutes
'0 */6 * * *'     # Every 6 hours
'0 0 * * *'       # Daily at midnight
'0 0 * * 0'       # Weekly on Sunday
'0 0 1 * *'       # Monthly on 1st
```

### Disable a Workflow

Two options:

**Option 1: GitHub UI**
1. Go to **Actions** tab
2. Click workflow name
3. Click **"•••"** menu → **"Disable workflow"**

**Option 2: Delete file**
```bash
rm .github/workflows/dexscraper.yml  # Or datafetch.yml
git commit -m "Disable workflow"
git push
```

---

## 📊 Usage Limits

### GitHub Actions Free Tier

- **2,000 minutes/month** for private repos
- **Unlimited** for public repos
- **6 hours max** per job

### Estimated Usage

**DexScreener (hourly):**
- ~2-3 minutes per run
- 24 runs/day × 30 days = 720 runs/month
- **Total: ~60-90 minutes/month**

**DataFetch (daily):**
- ~5-10 minutes per run (depends on token count)
- 30 runs/month
- **Total: ~150-300 minutes/month**

**Combined: ~210-390 minutes/month** (well within free tier!)

---

## 🐛 Troubleshooting

### Workflow Not Running

**Check:**
1. Actions are enabled (Settings → Actions → Allow all actions)
2. Secrets are added correctly (no typos)
3. Workflow files are in `.github/workflows/` directory
4. YAML syntax is valid (no tabs, proper indentation)

### Failed Runs

**Common issues:**

1. **Missing secrets** → Check Settings → Secrets
2. **Database connection failed** → Verify Supabase credentials
3. **Import errors** → Check `requirements.txt` has all dependencies
4. **Rate limiting** → DexScreener may throttle if too many requests

**To debug:**
1. Go to failed run in Actions tab
2. Expand each step to see error messages
3. Check logs for specific Python errors
4. Test locally first: `python run_dexscraper.py`

### Telegram Notifications Not Sending

**Check:**
1. `TELEGRAM_BOT_TOKEN` secret is correct
2. `TELEGRAM_CHAT_ID` secret is correct
3. Bot has permission to send messages to chat
4. Check workflow logs for Telegram API errors

---

## 🔐 Security Notes

- ✅ Secrets are encrypted and never shown in logs
- ✅ `.env` file is created temporarily and deleted after run
- ✅ Workflows run in isolated containers
- ⚠️ Never commit `.env` or secrets to git
- ⚠️ Add `.env` to `.gitignore`

---

## 📈 Monitoring

### Email Notifications

GitHub sends emails when workflows fail.

**To configure:**
1. GitHub Settings (your profile, not repo)
2. Notifications → Actions
3. Enable "Send notifications for failed workflows"

### Telegram Notifications

Both scripts send Telegram messages on completion:
- ✅ DexScreener: Reports tokens found/inserted
- ✅ DataFetch: Reports metrics collected

### View History

**Actions tab shows:**
- All workflow runs (past 90 days)
- Success/failure status
- Runtime duration
- Full logs

---

## 🎯 Next Steps

1. ✅ Set up GitHub secrets
2. ✅ Push code to GitHub
3. ✅ Test manual workflow run
4. ✅ Wait for scheduled run and verify
5. ✅ Monitor Telegram for notifications
6. ✅ Check Supabase for new data

**Optional enhancements:**
- Add error retry logic
- Set up status badges in README
- Create workflow for analyzing aged tokens
- Add workflow for Telegram alerts on high-score tokens

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax](https://crontab.guru/)
- [GitHub Actions Limits](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)

---

## 💡 Tips

- **Test locally first** before relying on GitHub Actions
- **Use workflow_dispatch** to manually trigger runs for testing
- **Check Actions usage** in Settings → Billing to track minutes
- **Set up branch protection** to prevent accidental workflow deletions
- **Use repository variables** for non-sensitive config (like chain_id)
