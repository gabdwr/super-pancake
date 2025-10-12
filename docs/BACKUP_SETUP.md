# Supabase Database Backup System

Automatic daily backups to GitHub with 30-day retention.

---

## 📦 What Gets Backed Up

The backup system exports your Supabase database to JSON files:

1. **`discovered_tokens_YYYYMMDD_HHMMSS.json`**
   - All tokens from the `discovered_tokens` table
   - Includes: token_address, chain_id, dexscreener_url, discovered_at

2. **`time_series_latest_YYYYMMDD_HHMMSS.json`**
   - Latest time-series snapshot for each token
   - Includes: All DexScreener metrics + GoPlus security data
   - Note: Full time-series history is NOT backed up (would be huge)

3. **`backup_info_YYYYMMDD_HHMMSS.json`**
   - Backup metadata (timestamp, counts, filenames)

---

## 🔧 Setup Instructions

### Step 1: Add GitHub Secrets

Your Supabase credentials are already in GitHub secrets (used by existing workflows), so backups will work automatically!

**Already configured:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase API key

### Step 2: Enable GitHub Actions (if not already enabled)

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/super-pancake`
2. Click **Settings** → **Actions** → **General**
3. Under "Workflow permissions", ensure:
   - ✅ "Read and write permissions" is selected
   - ✅ "Allow GitHub Actions to create and approve pull requests" is checked
4. Click **Save**

### Step 3: Test the Backup

**Option A: Manual trigger (recommended first time)**
1. Go to **Actions** tab in GitHub
2. Click **Daily Database Backup** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait ~1 minute for completion
5. Check the `backups/` folder in your repo

**Option B: Wait for automatic backup**
- Runs daily at 3 AM UTC automatically

---

## 📅 Backup Schedule

- **Frequency:** Daily at 3:00 AM UTC
- **Retention:** Last 30 days (older backups auto-deleted)
- **Location:** `backups/` folder in your GitHub repo

---

## 🔄 How to Restore from Backup

### Restore discovered_tokens table

```python
import json
from src.database.supabase_rest import SupabaseREST

# Load backup
with open('backups/discovered_tokens_20250414_030000.json') as f:
    tokens = json.load(f)

# Restore to Supabase
supabase = SupabaseREST()
for token in tokens:
    supabase.store_discovered_tokens([token])
```

### Restore time_series_data

```python
import json
from src.database.supabase_rest import SupabaseREST

# Load backup
with open('backups/time_series_latest_20250414_030000.json') as f:
    snapshots = json.load(f)

# Restore to Supabase
supabase = SupabaseREST()
for snapshot in snapshots:
    supabase.store_time_series_data(
        metrics_data=snapshot,
        token_address=snapshot['token_address'],
        chain_id=snapshot['chain_id']
    )
```

### Quick restore script

```bash
# Download specific backup from GitHub
wget https://raw.githubusercontent.com/YOUR_USERNAME/super-pancake/main/backups/discovered_tokens_20250414_030000.json

# Run restore (you would create a restore script)
python scripts/restore_backup.py discovered_tokens_20250414_030000.json
```

---

## 🧪 Test Backup Manually

Run the backup script locally:

```bash
cd ~/Documents/super-pancake
python scripts/backup_supabase.py
```

Output:
```
🚀 Starting Supabase backup...
📦 Backing up discovered_tokens table...
✅ Backed up 167 tokens to discovered_tokens_20250414_153022.json
📦 Backing up time_series_data (latest snapshots)...
✅ Backed up 167 time-series snapshots to time_series_latest_20250414_153022.json
✅ Backup metadata saved to backup_info_20250414_153022.json
======================================================================
✅ Backup complete!
   📁 Directory: /home/luke/Documents/super-pancake/backups
   📊 Tokens: 167
   📈 Time-series snapshots: 167
   📝 Files created:
      - discovered_tokens_20250414_153022.json
      - time_series_latest_20250414_153022.json
      - backup_info_20250414_153022.json
======================================================================
```

---

## 🚨 Important Notes

### What's NOT backed up:
- **Full time-series history** - Only latest snapshot per token
  - Reason: Full history could be 100MB+ and grow rapidly
  - Solution: If you need full history, use Supabase's native backups ($25/mo)

### Storage limits:
- **GitHub repository limit:** 1 GB recommended, 5 GB hard limit
- **Current size:** ~11 MB total database
- **Estimated backup size:** ~2-3 MB per day (compressed JSON)
- **30-day retention:** ~60-90 MB total

You have plenty of space for the next several months!

### Backup file format:
Files are JSON for easy inspection and portability. You can:
- View them directly in GitHub
- Parse them with any programming language
- Import into Excel/Google Sheets
- Query with `jq` command-line tool

---

## 📊 Monitor Backups

### Check backup status:
1. Go to **Actions** tab in GitHub
2. Look for green checkmarks on "Daily Database Backup" workflow
3. Click on any run to see logs

### Check backup files:
1. Browse to `backups/` folder in your repo
2. Files are named with timestamps
3. Each backup creates 3 files

### Check backup size:
```bash
cd backups/
ls -lh *.json | awk '{print $5, $9}'
```

---

## 🆘 Troubleshooting

### Backup workflow fails with "permission denied"
**Fix:** Enable write permissions in Settings → Actions → General → Workflow permissions

### No new backups appearing
**Check:**
1. GitHub Actions is enabled for your repo
2. Secrets `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set
3. Workflow file exists: `.github/workflows/backup.yml`
4. Check Actions tab for error logs

### Backup files too large
**Solution:** The cleanup job runs automatically, but you can manually delete old files:
```bash
cd backups/
rm *_202501*.json  # Delete all January backups
git add . && git commit -m "Clean up old backups" && git push
```

---

## 🔐 Security

- Backup files contain sensitive data (token addresses, metrics)
- Stored in **private GitHub repository** only
- Never commit `.env` file (contains API keys)
- Supabase credentials stored as GitHub Secrets (encrypted)

---

## 📈 Future Improvements

If your database grows beyond GitHub limits:

1. **Compress backups** - Add gzip compression (10x smaller)
2. **Use Git LFS** - Store large files efficiently
3. **Switch to cloud storage** - Google Drive (15 GB free) or AWS S3
4. **Selective backups** - Only backup recent data (last 30 days of time-series)
5. **Incremental backups** - Only backup changes since last backup

---

## ✅ Quick Start Checklist

- [ ] GitHub Actions enabled with write permissions
- [ ] Secrets `SUPABASE_URL` and `SUPABASE_ANON_KEY` configured
- [ ] Test backup manually: `python scripts/backup_supabase.py`
- [ ] Trigger first GitHub Actions backup manually
- [ ] Verify backup files appear in `backups/` folder
- [ ] Check backup runs successfully next day at 3 AM UTC

Done! Your database is now backed up daily to GitHub. 🎉
