# Actually Free Hosting Options (2025 Update)

**TL;DR:** Railway and Render are NO LONGER FREE. Here are the truly free alternatives.

## The Problem

As of 2025:
- **Render.com**: Cron jobs cost minimum $1/month
- **Railway.app**: Only $5 trial credit (30 days), then $1/month credit (not enough)
- **Oracle Cloud**: Free VMs, but unreliable (random shutdowns as you experienced)

## Truly Free Solutions

### Option 1: GitHub Actions (Public Repo) ⭐ BEST OPTION

**Cost:** $0 forever (unlimited for public repos)

**Important:** GitHub Actions is completely FREE and UNLIMITED for **public repositories**. The 2,000 minute limit only applies to **private repos** on the free tier.

**Your repo:** https://github.com/gabdwr/super-pancake

**Is it public?** Check your repo settings at https://github.com/gabdwr/super-pancake/settings

If **public**: You have unlimited GitHub Actions - just keep using it!
If **private**: You hit the 2,000 min/month limit (~30 hours)

**To repo public (if it's private):**
1. Go to https://github.com/gabdwr/super-pancake/settings
2. Scroll to bottom → "Danger Zone"
3. Click "Change visibility" → "Make public"
4. Confirmmake 

**⚠️ Before making public:**
- Make sure no secrets (.env files) are committed
- Ensure no sensitive API keys in code
- Your trading strategy will be visible (but your actual trades won't be)

**After making public:**
- Unlimited GitHub Actions minutes
- Your workflow will just work again
- No need to migrate anywhere!

---

### Option 2: Cron-job.org + Free Web Hosting

**Cost:** $0 forever

**How it works:**
1. Deploy a simple web endpoint (Flask app) somewhere free
2. Use cron-job.org to ping it every hour
3. Web endpoint triggers your Python script

**Free hosting options for web endpoint:**
- **Vercel** (best): Free hobby plan, never sleeps
- **Fly.io**: 3 shared-cpu VMs free
- **Koyeb**: Free tier with 512MB RAM

**Setup:**
1. Use the `railway_web.py` file I already created
2. Deploy to Vercel/Fly.io/Koyeb
3. Get your deployment URL (e.g., https://yourapp.vercel.app)
4. Sign up at cron-job.org (free, 300 executions/day)
5. Create job to ping https://yourapp.vercel.app/trigger every hour

**Vercel setup (easiest):**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from your project directory
vercel --prod

# Add environment variables in Vercel dashboard
```

**Vercel free tier:**
- 100 GB bandwidth/month
- 100 GB-hours compute time/month
- Your usage: ~5 min/hour × 24 hours = 2 GB-hours/month
- **Verdict:** Well within limits

---

### Option 3: Local Machine + cron

**Cost:** $0 (just electricity)

**Setup:**
```bash
# Edit crontab
crontab -e

# Add this line
30 * * * * cd /home/luke/Documents/super-pancake && source venv/bin/activate && python run_datafetch_and_filtration.py >> logs/cron.log 2>&1
```

**Pros:**
- Works immediately
- Full control
- No external dependencies

**Cons:**
- Machine must stay on 24/7
- No built-in monitoring
- Vulnerable to power outages/reboots

**Best for:** Development/testing, temporary solution

---

### Option 4: Google Cloud Run + Cloud Scheduler

**Cost:** $0 (within generous free tier)

**Free tier:**
- Cloud Run: 2 million requests/month, 360,000 GB-seconds compute
- Cloud Scheduler: 3 free jobs per month
- Your usage: 720 executions/month × 5 min = well within limits

**Setup:**
```bash
# 1. Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# 2. Initialize
gcloud init

# 3. Create Dockerfile (simple)
cat > Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_datafetch_and_filtration.py"]
EOF

# 4. Deploy to Cloud Run
gcloud run deploy token-datafetch \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=$SUPABASE_URL,SUPABASE_KEY=$SUPABASE_KEY"

# 5. Create Cloud Scheduler job
gcloud scheduler jobs create http token-datafetch-hourly \
  --schedule "30 * * * *" \
  --uri "https://token-datafetch-xxxxx.run.app" \
  --http-method POST \
  --oidc-service-account-email YOUR_SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com
```

**Pros:**
- Truly free (Google Cloud free tier is generous)
- Professional infrastructure
- Native cron support
- Reliable

**Cons:**
- More complex setup
- Requires Google account

---

### Option 5: AWS Lambda + EventBridge (Free Tier)

**Cost:** $0 (within free tier)

**Free tier:**
- Lambda: 1 million requests/month, 400,000 GB-seconds compute
- EventBridge: 14 million events/month free
- Your usage: 720 executions/month = well within limits

**Setup:**
1. Create Lambda function from your Python code
2. Package dependencies in Lambda Layer
3. Create EventBridge rule: `cron(30 * * * ? *)`
4. Connect rule to Lambda function

**Pros:**
- Generous free tier
- Serverless (no servers to manage)
- Reliable

**Cons:**
- AWS complexity
- 15-minute Lambda timeout (your script is ~5 min, so OK)

---

## Decision Tree

```
Is your GitHub repo public or can you make it public?
├─ YES → Use GitHub Actions (Option 1) ⭐
│        Unlimited, free forever, already set up
│
└─ NO (must stay private)
   │
   ├─ Want easiest setup? → Vercel + cron-job.org (Option 2)
   │                         5 minutes, free forever
   │
   ├─ Have Google account? → Google Cloud Run (Option 4)
   │                         Professional, free, reliable
   │
   ├─ Have AWS account? → AWS Lambda (Option 5)
   │                      Serverless, free tier
   │
   └─ Need immediate solution? → Local cron (Option 3)
                                  Works right now, but machine must stay on
```

## My Recommendation

### 1st Choice: Make GitHub repo public
- Your repo: https://github.com/gabdwr/super-pancake
- Check if it's already public
- If not, make it public (after removing any secrets)
- **Result:** Unlimited free GitHub Actions forever

### 2nd Choice: Vercel + cron-job.org
- Easiest if repo must stay private
- 5-minute setup
- Free forever
- Reliable

### 3rd Choice: Local cron
- Immediate solution
- Use while you set up Vercel
- Keep machine running 24/7

## Check Your GitHub Repo Visibility

Run this to check if your repo is public:
```bash
# Install GitHub CLI (if not already)
# Ubuntu/Debian: sudo apt install gh
# Mac: brew install gh

# Check repo visibility
gh repo view gabdwr/super-pancake --json visibility -q .visibility
```

If it says "public" → You're good! GitHub Actions is unlimited for you!
If it says "private" → You need an alternative (Vercel recommended)

## Next Steps

1. ✅ Check if repo is public or private
2. ✅ If public: Keep using GitHub Actions (you have unlimited minutes!)
3. ✅ If private: Choose between making it public OR using Vercel + cron-job.org
4. ✅ Deploy and test at next :30 hour mark

---

**Bottom line:** Check your repo visibility first. If it's public (or you can make it public), you already have the best solution - unlimited GitHub Actions!
