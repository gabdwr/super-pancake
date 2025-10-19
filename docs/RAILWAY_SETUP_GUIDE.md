# Railway.app Setup Guide (Recommended)

**Why Railway?** After Oracle Cloud VM reliability issues, Railway is the best alternative - professional infrastructure, easy setup, and sufficient free tier for hourly cron jobs.

## Quick Setup (5 minutes)

### 1. Prepare Your Repository

First, create a simple start script that Railway will run:

**Create `railway_cron.sh`:**
```bash
#!/bin/bash
cd /app
source venv/bin/activate
python run_datafetch_and_filtration.py
```

**Create `railway.json`** (tells Railway how to run your cron):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash railway_cron.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 2. Sign Up & Deploy

1. Go to https://railway.app
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Authorize Railway to access your repo
5. Select your `super-pancake` repository

### 3. Add Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Set Up Cron (Important!)

Railway doesn't have built-in cron, but we can use an external cron service to ping Railway:

**Option A: Use cron-job.org (Free)**

1. Go to https://cron-job.org and sign up
2. Create a new cron job:
   - **URL**: Your Railway deployment URL + `/trigger` endpoint
   - **Schedule**: `30 * * * *` (every hour at :30)
   - **Title**: "Token Datafetch Hourly"

3. Add a simple Flask endpoint to your code (see below)

**Option B: Railway Cron Plugin (Paid, but reliable)**

1. In Railway dashboard, click "New" → "Plugin" → "Cron"
2. Set schedule: `30 * * * *`
3. Set command: `bash railway_cron.sh`
4. Costs ~$1-2/month but very reliable

### 5. Add HTTP Trigger Endpoint (for Option A)

If using cron-job.org, you need an HTTP endpoint to trigger your script.

**Create `railway_web.py`:**
```python
from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_datafetch():
    """HTTP endpoint to trigger datafetch via external cron service"""
    try:
        result = subprocess.run(
            ['python', 'run_datafetch_and_filtration.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )

        return jsonify({
            'status': 'success',
            'output': result.stdout[-500:] if result.stdout else '',  # Last 500 chars
            'returncode': result.returncode
        }), 200
    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Timeout after 5 minutes'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

**Update `requirements.txt`:**
```
flask>=3.0.0
```

**Update `railway.json` start command:**
```json
{
  "deploy": {
    "startCommand": "python railway_web.py"
  }
}
```

## Alternative: Render.com (Native Cron)

If you prefer native cron without webhooks:

1. Go to https://render.com
2. Create new "Cron Job" (not Web Service)
3. Connect your GitHub repo
4. Set schedule: `30 * * * *`
5. Set command: `python run_datafetch_and_filtration.py`
6. Add environment variables
7. Free tier: 750 hours/month

**Pros:** Native cron support, no webhook needed
**Cons:** Slower cold starts than Railway

## Monitoring Your Deployment

### Railway Dashboard:
- **Logs**: Real-time logs of your script execution
- **Metrics**: CPU, memory, network usage
- **Deployments**: See build status and history

### Check if it's working:
1. Watch Railway logs at next :30 mark
2. Check your Telegram for summary messages
3. Query Supabase to see new time_series_data rows

### Troubleshooting:

**Build fails:**
- Check that `requirements.txt` includes all dependencies
- Ensure Python 3.11 is specified (Railway auto-detects)

**Cron not triggering:**
- Verify cron-job.org schedule is correct (UTC time!)
- Check that your Railway app URL is publicly accessible
- Test `/trigger` endpoint manually in browser

**Script errors:**
- Check Railway logs for Python errors
- Ensure environment variables are set correctly
- Verify Supabase connection works from Railway IP

## Cost Estimate

**Railway Free Tier:**
- 500 hours/month execution time
- $5 starter credit
- Your hourly job: ~5 min execution = 2.5 hours/month
- **Verdict:** Completely free for your use case

**If you exceed free tier:**
- ~$0.000463/minute = ~$0.002/execution
- 720 executions/month = ~$1.44/month
- Still very cheap!

## Recommended Setup

For maximum reliability without complexity:

1. ✅ Use Railway for hosting (reliable, easy)
2. ✅ Use cron-job.org for scheduling (free, external)
3. ✅ Add Flask endpoint for HTTP triggers (simple)
4. ✅ Monitor via Railway dashboard + Telegram alerts

This gives you:
- No VM management headaches (unlike Oracle)
- Professional infrastructure
- Easy monitoring and debugging
- Completely free for your usage pattern

## Next Steps

1. Create the Flask endpoint (`railway_web.py`)
2. Update `requirements.txt` to include Flask
3. Push changes to GitHub
4. Deploy to Railway
5. Set up cron-job.org to ping your Railway URL
6. Monitor first execution at :30

---

**Need help?** Railway has excellent docs at https://docs.railway.app
