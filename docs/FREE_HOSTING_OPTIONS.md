# Free Alternatives to GitHub Actions

You've hit GitHub Actions free tier limits. Here are free alternatives to run your hourly datafetch:

---

## ✅ Option 1: Railway.app (RECOMMENDED - Easiest)

**Free Tier:** 500 hours/month + $5 credit
**Perfect for:** Running cron jobs 24/7

### Setup:
1. **Create account:** https://railway.app (sign in with GitHub)
2. **Deploy from GitHub repo:**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `super-pancake` repo

3. **Add Cron Service:**
   ```bash
   # Create Procfile in repo root
   echo "worker: while true; do python run_datafetch_and_filtration.py && sleep 3600; done" > Procfile
   ```

4. **Add environment variables in Railway dashboard:**
   - `SUPABASE_HOST`
   - `SUPABASE_PORT`
   - `SUPABASE_USERNAME`
   - `SUPABASE_PASSWORD`
   - `SUPABASE_DBNAME`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

**Pros:**
- ✅ Easy setup (5 minutes)
- ✅ Auto-deploys on git push
- ✅ Generous free tier
- ✅ Built-in logging

**Cons:**
- ⚠️ $5/month credit runs out eventually (but renews)

---

## ✅ Option 2: Oracle Cloud Free Tier (BEST - Truly Free Forever)

**Free Tier:** 2 AMD VMs free FOREVER (not trial)
**Perfect for:** Full control, unlimited runtime

### Setup:
1. **Create account:** https://www.oracle.com/cloud/free/
   - Choose "Always Free" tier
   - Requires credit card (won't be charged)

2. **Create VM Instance:**
   - Compute → Instances → Create Instance
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (Always Free)

3. **SSH into VM:**
   ```bash
   ssh ubuntu@<your-vm-ip>
   ```

4. **Install dependencies:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip -y

   # Clone your repo
   git clone https://github.com/yourusername/super-pancake.git
   cd super-pancake

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

5. **Create .env file:**
   ```bash
   nano .env
   # Paste your environment variables
   ```

6. **Setup cron:**
   ```bash
   crontab -e

   # Add this line (runs every hour at :30)
   30 * * * * cd /home/ubuntu/super-pancake && /home/ubuntu/super-pancake/venv/bin/python run_datafetch_and_filtration.py >> /home/ubuntu/logs/datafetch.log 2>&1

   # Create logs directory
   mkdir -p /home/ubuntu/logs
   ```

7. **Test it works:**
   ```bash
   cd /home/ubuntu/super-pancake
   source venv/bin/activate
   python run_datafetch_and_filtration.py
   ```

**Pros:**
- ✅ **100% FREE FOREVER**
- ✅ Full control (root access)
- ✅ Can run other services too
- ✅ No time limits

**Cons:**
- ⚠️ Requires more technical setup (20-30 min)
- ⚠️ Need to manage updates yourself

---

## ✅ Option 3: Render.com

**Free Tier:** 750 hours/month
**Perfect for:** Cron jobs

### Setup:
1. **Create account:** https://render.com
2. **Create Cron Job:**
   - Dashboard → New → Cron Job
   - Connect GitHub repo
   - Command: `python run_datafetch_and_filtration.py`
   - Schedule: `30 * * * *` (every hour at :30)

3. **Add environment variables** in Render dashboard

**Pros:**
- ✅ Easy setup
- ✅ Native cron job support
- ✅ Auto git pull on deploy

**Cons:**
- ⚠️ 750 hours/month = ~31 days (cutting it close)

---

## ✅ Option 4: Fly.io

**Free Tier:** 3 VMs free
**Perfect for:** Long-running processes

### Setup:
1. **Install flyctl:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   flyctl auth login
   ```

3. **Create fly.toml in repo:**
   ```toml
   app = "super-pancake-datafetch"

   [build]

   [processes]
   worker = "while true; do python run_datafetch_and_filtration.py && sleep 3600; done"

   [[services]]
   internal_port = 8080
   protocol = "tcp"
   ```

4. **Deploy:**
   ```bash
   flyctl launch
   flyctl secrets set SUPABASE_HOST=xxx SUPABASE_PORT=xxx ...
   flyctl deploy
   ```

**Pros:**
- ✅ Easy CLI deployment
- ✅ Generous free tier

**Cons:**
- ⚠️ Requires Dockerfile

---

## ✅ Option 5: Your Local Machine (Simplest)

**Free Tier:** Unlimited (if you have a computer running 24/7)
**Perfect for:** Testing, development

### Setup (Linux/Mac):
```bash
# Edit crontab
crontab -e

# Add this line
30 * * * * cd /home/luke/Documents/super-pancake && /usr/bin/python3 run_datafetch_and_filtration.py >> /home/luke/logs/datafetch.log 2>&1

# Create logs directory
mkdir -p /home/luke/logs
```

### Setup (Windows):
1. Open **Task Scheduler**
2. Create Task → Trigger: Hourly at :30
3. Action: Start Program
   - Program: `python.exe`
   - Arguments: `run_datafetch_and_filtration.py`
   - Start in: `C:\path\to\super-pancake`

**Pros:**
- ✅ 100% free
- ✅ Full control
- ✅ Instant setup

**Cons:**
- ⚠️ Computer must run 24/7
- ⚠️ Uses your electricity/internet

---

## 📊 Comparison Table

| Service | Free Tier | Setup Time | Forever Free? | Best For |
|---------|-----------|------------|---------------|----------|
| **Railway** | 500h/mo + $5 credit | 5 min | ⚠️ Credit runs out | Easiest |
| **Oracle Cloud** | 2 VMs forever | 30 min | ✅ YES | Best value |
| **Render** | 750h/mo | 10 min | ✅ YES | Simple cron |
| **Fly.io** | 3 VMs | 15 min | ✅ YES | Docker fans |
| **Local Machine** | Unlimited | 2 min | ✅ YES | Testing |

---

## 🎯 My Recommendation

### For You (Quick & Easy):
**Use Railway.app** - Takes 5 minutes to set up, just works.

### For Long-term (Best Value):
**Use Oracle Cloud** - Free forever, unlimited. Worth the 30 min setup.

### For Right Now (Immediate):
**Use your local machine** - Set up cron in 2 minutes while you decide on cloud hosting.

---

## 🚀 Quick Start Script (Oracle Cloud)

I'll create a setup script for you:

```bash
#!/bin/bash
# Oracle Cloud VM Setup Script
# Run this after SSH into your VM

set -e

echo "🚀 Setting up Super Pancake on Oracle Cloud..."

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Python
echo "🐍 Installing Python 3.11..."
sudo apt install python3.11 python3.11-venv python3-pip git -y

# Clone repo
echo "📂 Cloning repository..."
cd ~
git clone https://github.com/yourusername/super-pancake.git
cd super-pancake

# Setup venv
echo "🔧 Setting up virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "⚙️ Creating .env file..."
cat > .env << 'EOF'
SUPABASE_HOST=your_host_here
SUPABASE_PORT=5432
SUPABASE_USERNAME=your_username_here
SUPABASE_PASSWORD=your_password_here
SUPABASE_DBNAME=your_dbname_here
SUPABASE_URL=your_url_here
SUPABASE_ANON_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF

echo "⚠️  IMPORTANT: Edit .env file with your actual credentials!"
echo "Run: nano .env"
echo ""

# Create logs directory
mkdir -p ~/logs

# Setup cron
echo "⏰ Setting up cron job..."
(crontab -l 2>/dev/null; echo "30 * * * * cd $HOME/super-pancake && $HOME/super-pancake/venv/bin/python run_datafetch_and_filtration.py >> $HOME/logs/datafetch.log 2>&1") | crontab -

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials: nano .env"
echo "2. Test the script: source venv/bin/activate && python run_datafetch_and_filtration.py"
echo "3. Check logs: tail -f ~/logs/datafetch.log"
echo ""
echo "Cron job is set to run every hour at :30"
```

---

## 📞 Need Help?

**Oracle Cloud setup issue?** Check the firewall/security groups
**Railway not deploying?** Check build logs in dashboard
**Cron not running?** Check with `crontab -l` and `tail -f ~/logs/datafetch.log`

Let me know which option you want to go with and I can provide detailed setup instructions! 🚀
