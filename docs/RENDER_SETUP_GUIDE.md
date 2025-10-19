# Render.com Setup Guide (Simplest Option)

**Why Render?** Native cron job support - no webhooks, no external services needed. Just pure cron scheduling like you'd expect. Perfect replacement for GitHub Actions.

## Setup (3 minutes)

### 1. Sign Up

1. Go to https://render.com
2. Sign up with GitHub (easiest)
3. Authorize Render to access your repos

### 2. Create Cron Job

1. Click "New +" → "Cron Job"
2. **Repository**: Select `super-pancake`
3. **Name**: `token-datafetch-hourly`
4. **Region**: Oregon (US West) - fastest for most users
5. **Branch**: `main` (or your default branch)
6. **Build Command**: Leave empty (Render auto-detects Python)
7. **Command**: `python run_datafetch_and_filtration.py`
8. **Schedule**: Custom → `30 * * * *`
   - This means: "At minute 30 of every hour"
   - Render uses UTC time (keep this in mind!)

### 3. Add Environment Variables

In the "Environment" section, click "Add Environment Variable" for each:

```
SUPABASE_URL = your_supabase_url
SUPABASE_KEY = your_supabase_key
TELEGRAM_BOT_TOKEN = your_telegram_token
TELEGRAM_CHAT_ID = your_chat_id
```

### 4. Deploy

1. Click "Create Cron Job"
2. Render will build your environment
3. First run will happen at next :30 mark

That's it! No Flask server, no webhooks, no external cron services.

## Monitoring

### View Logs:
1. Go to your cron job dashboard
2. Click "Logs" tab
3. See real-time output from your script

### Check Execution History:
1. Click "Events" tab
2. See all past runs with timestamps
3. Success/failure status for each run

### Manual Trigger:
1. Click "Manual Deploy" → "Deploy latest commit"
2. Useful for testing without waiting for :30

## Troubleshooting

**Build fails:**
- Check that Python version is detected correctly (should auto-detect from runtime.txt or code)
- Verify all dependencies in requirements.txt are installable
- Check build logs for specific errors

**Cron doesn't run:**
- Verify schedule syntax: `30 * * * *`
- Remember Render uses UTC time
- Check "Events" tab to see if job attempted to run

**Script errors:**
- Check "Logs" tab for Python traceback
- Ensure environment variables are set
- Test locally first with same .env values

## Cost Estimate

**Render Free Tier:**
- 750 hours/month for cron jobs
- Your usage: ~5 min/execution × 720 executions = 60 hours/month
- **Verdict:** Completely free, uses only 8% of quota

**If you exceed free tier:**
- $7/month for Starter plan (unlimited hours)
- Very unlikely you'll need this

## Comparison: Render vs Railway

| Feature | Render | Railway |
|---------|--------|---------|
| **Native Cron** | ✅ Yes | ❌ No (need webhook) |
| **Setup Time** | 3 min | 5 min |
| **Complexity** | Simple | Medium (Flask + cron-job.org) |
| **Free Hours** | 750/mo | 500/mo |
| **Monitoring** | Built-in | Built-in |
| **Reliability** | Excellent | Excellent |

**Recommendation:** Use Render if you want simplicity. Use Railway if you need more flexibility later.

## Next Steps

1. ✅ Sign up at render.com
2. ✅ Create new Cron Job
3. ✅ Connect your GitHub repo
4. ✅ Set command: `python run_datafetch_and_filtration.py`
5. ✅ Set schedule: `30 * * * *`
6. ✅ Add environment variables
7. ✅ Deploy and monitor first run

---

**This is probably your best option** - native cron, no complexity, just works.
