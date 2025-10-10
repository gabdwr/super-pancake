# 🥞 Super Pancake - Setup Checklist

**Status:** You have API keys! Now let's get everything configured.

---

## ✅ What You Already Have

- ✅ Moralis API key
- ✅ Alchemy BSC RPC URL
- ✅ Project documentation (START_HERE.md, PROJECT_PLAN.md, TASK_LIST.md)
- ✅ `.env` file created with your keys
- ✅ Directory structure created

---

## 📋 Setup Steps (15-30 minutes)

### Step 1: Verify Python Version ⬜

```bash
python3 --version
```

**Required:** Python 3.10 or higher

**If you have < 3.10:**
- Download from https://www.python.org/downloads/
- Or use pyenv: `pyenv install 3.10`

### Step 2: Create Virtual Environment ⬜

```bash
cd ~/Documents/super-pancake
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Verify:**
```bash
which python
# Should show: /home/luke/Documents/super-pancake/venv/bin/python
```

### Step 3: Install Dependencies ⬜

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If `ta-lib` fails to install:
```bash
# Ubuntu/Debian
sudo apt-get install libta-lib0-dev
pip install ta-lib

# Mac
brew install ta-lib
pip install ta-lib

# Or skip it for now (it's optional)
# Edit requirements.txt and comment out: # ta-lib>=0.4.28
```

**Verify:**
```bash
pip list | grep -E "web3|requests|pandas"
# Should see all packages installed
```

### Step 4: Test API Connections ⬜

```bash
python scripts/test_apis.py
```

**Expected Output:**
```
DexScreener         ✅ PASS
GoPlus              ✅ PASS
Moralis             ✅ PASS
Alchemy             ✅ PASS

🎉 ALL APIs WORKING!
```

**If any fail:**
- DexScreener/GoPlus: Check internet connection
- Moralis: Check `MORALIS_API_KEY` in `.env`
- Alchemy: Check `ALCHEMY_BSC_RPC` in `.env`

### Step 5: Install PostgreSQL ⬜

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Mac:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Run installer, remember the password you set

**Verify:**
```bash
psql --version
# Should show: psql (PostgreSQL) 14.x or higher
```

### Step 6: Create Database ⬜

```bash
# Login as postgres user
sudo -u postgres psql

# Run these commands in psql:
CREATE DATABASE superpancake;
CREATE USER pancake_user WITH PASSWORD 'choose_a_strong_password';
GRANT ALL PRIVILEGES ON DATABASE superpancake TO pancake_user;
\q  # Exit psql
```

**Update `.env` file:**
```env
DATABASE_URL=postgresql://pancake_user:your_chosen_password@localhost:5432/superpancake
```

**Verify:**
```bash
psql -U pancake_user -d superpancake -h localhost
# Should connect (will prompt for password)
\q  # Exit
```

### Step 7: Delete keys.py (Security) ⬜

**Important:** Your keys are now in `.env` (which is in `.gitignore`)

```bash
rm keys.py
git status
# Verify keys.py is NOT shown (it's in .gitignore)
```

### Step 8: Test Everything Together ⬜

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Test APIs
python scripts/test_apis.py

# Test GoPlus specifically
python scripts/test_goplus.py

# Try importing packages
python -c "import web3, requests, pandas; print('✅ All imports working!')"
```

---

## 🎯 You're Done When...

- ✅ Python 3.10+ installed
- ✅ Virtual environment activated
- ✅ All dependencies installed (requirements.txt)
- ✅ API test script shows all PASS
- ✅ PostgreSQL installed and database created
- ✅ `.env` file has correct keys
- ✅ `keys.py` deleted (security)

---

## 🚀 What's Next?

### Option 1: Start Building (Recommended)
Open **[TASK_LIST.md](TASK_LIST.md)** and jump to **Phase 2: Token Discovery**

```bash
# Create your first module
mkdir -p src/discovery
touch src/discovery/__init__.py
touch src/discovery/dexscreener.py

# Start coding!
nano src/discovery/dexscreener.py
```

### Option 2: Read More First
- **[START_HERE.md](START_HERE.md)** - 7-day roadmap
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Deep dive on architecture and trading concepts
- **[README.md](README.md)** - Project overview and FAQ

---

## 📊 Quick Reference

### Activate Virtual Environment
```bash
cd ~/Documents/super-pancake
source venv/bin/activate
```

### Run Tests
```bash
python scripts/test_apis.py      # Test all APIs
python scripts/test_goplus.py    # Test GoPlus specifically
```

### Check API Rate Limits
| API | Free Tier | Your Usage | Status |
|-----|-----------|------------|--------|
| **DexScreener** | Unlimited | 10-50/day | ✅ Plenty |
| **GoPlus** | 30/min (43K/day) | 10-50/day | ✅ Plenty |
| **Moralis** | 40K CU/day | ~500-1K/day | ✅ Plenty |
| **Alchemy** | 100M CU/month | ~50K/day | ✅ Plenty |

**Bottom Line:** All free tiers are MORE than sufficient for this project!

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### "psycopg2 won't install"
```bash
# Try the binary version
pip install psycopg2-binary
```

### "Can't connect to PostgreSQL"
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start it if not running
sudo systemctl start postgresql
```

### "API test fails with 401/403"
```bash
# Check .env file has correct keys
cat .env | grep API_KEY

# Make sure no extra spaces around the = sign
# Good: MORALIS_API_KEY=your_key
# Bad:  MORALIS_API_KEY = your_key
```

### "python-dotenv not loading .env"
```bash
# Make sure .env is in project root
ls -la .env

# Test loading manually
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('MORALIS_API_KEY'))"
```

---

## 💡 Pro Tips

1. **Always activate venv first:** Get in the habit of `source venv/bin/activate` before running any Python commands

2. **Check .env often:** If APIs fail, 90% of the time it's a typo in `.env`

3. **Use tmux/screen:** When developing, use `tmux` to keep multiple terminals open (one for code, one for tests, one for logs)

4. **Git commit frequently:** After each working feature:
   ```bash
   git add .
   git commit -m "Added DexScreener API integration"
   ```

5. **Test incrementally:** Don't write 100 lines before testing. Write 10 lines, test, repeat.

---

## 📅 Estimated Timeline

| Task | Time | Status |
|------|------|--------|
| Python + venv setup | 5 min | ⬜ |
| Install dependencies | 5-10 min | ⬜ |
| Test APIs | 2 min | ⬜ |
| Install PostgreSQL | 5-15 min | ⬜ |
| Create database | 3 min | ⬜ |
| Clean up keys.py | 1 min | ⬜ |
| **Total** | **15-30 min** | |

---

**Ready to build?** Run through this checklist, then open [TASK_LIST.md](TASK_LIST.md) and start Phase 2! 🚀
