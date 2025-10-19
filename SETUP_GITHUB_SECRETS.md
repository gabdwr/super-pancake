# Setup GitHub Secrets - Quick Guide

Your code is ready! Now you need to add your filter strategy values to GitHub Secrets.

## Step 1: Copy Your Filter Values

From your `.env` file, you need these 7 values:

```bash
# Run this command to see your current values:
grep "^FILTER_" /home/luke/Documents/super-pancake/.env
```

You should see something like:
```
FILTER_ALLOW_HONEYPOT=False
FILTER_MIN_LP_LOCKED=30
FILTER_MIN_CONCENTRATION=50
FILTER_MIN_LIQUIDITY_USD=20000
FILTER_MAX_BUY_TAX=10
FILTER_MAX_SELL_TAX=10
FILTER_ALLOW_MINTABLE=False
```

## Step 2: Add to GitHub Secrets

1. **Go to your repository secrets page:**
   https://github.com/gabdwr/super-pancake/settings/secrets/actions

2. **Click "New repository secret"**

3. **Add each secret one by one:**

### Secret 1: FILTER_ALLOW_HONEYPOT
- Name: `FILTER_ALLOW_HONEYPOT`
- Value: `False`

### Secret 2: FILTER_MIN_LP_LOCKED
- Name: `FILTER_MIN_LP_LOCKED`
- Value: `30`

### Secret 3: FILTER_MIN_CONCENTRATION
- Name: `FILTER_MIN_CONCENTRATION`
- Value: `50`

### Secret 4: FILTER_MIN_LIQUIDITY_USD
- Name: `FILTER_MIN_LIQUIDITY_USD`
- Value: `20000`

### Secret 5: FILTER_MAX_BUY_TAX
- Name: `FILTER_MAX_BUY_TAX`
- Value: `10`

### Secret 6: FILTER_MAX_SELL_TAX
- Name: `FILTER_MAX_SELL_TAX`
- Value: `10`

### Secret 7: FILTER_ALLOW_MINTABLE
- Name: `FILTER_ALLOW_MINTABLE`
- Value: `False`

## Step 3: Verify Secrets Are Set

After adding all 7 secrets, you should see them listed at:
https://github.com/gabdwr/super-pancake/settings/secrets/actions

The list should show:
- ✅ FILTER_ALLOW_HONEYPOT
- ✅ FILTER_ALLOW_MINTABLE
- ✅ FILTER_MAX_BUY_TAX
- ✅ FILTER_MAX_SELL_TAX
- ✅ FILTER_MIN_CONCENTRATION
- ✅ FILTER_MIN_LP_LOCKED
- ✅ FILTER_MIN_LIQUIDITY_USD
- Plus your existing secrets (SUPABASE_*, TELEGRAM_*, etc.)

## Step 4: Make Repository Public (Optional)

If you want unlimited GitHub Actions:

1. Go to: https://github.com/gabdwr/super-pancake/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"
4. Select "Make public"
5. Confirm

**Result:** Unlimited GitHub Actions minutes forever!

## Step 5: Test

Wait for the next :30 minute mark (e.g., 2:30, 3:30, 4:30...)

Watch your workflow run:
https://github.com/gabdwr/super-pancake/actions

Check the logs for:
```
🔧 Critical Filters Configuration:
   Allow Honeypot: False
   Min LP Locked: 30.0%
   Min Concentration: 50.0
   Min Liquidity: $20,000
   Max Buy Tax: 10.0%
   Max Sell Tax: 10.0%
   Allow Mintable: False
```

## Troubleshooting

### Workflow uses default values (not my secrets)

**Problem:** Logs show default values, not your configured values

**Solution:** GitHub Secrets not set or named incorrectly

1. Check secrets page: https://github.com/gabdwr/super-pancake/settings/secrets/actions
2. Verify all 7 `FILTER_*` secrets exist
3. Verify names are EXACTLY as shown above (case-sensitive)
4. Re-run workflow from Actions tab

### How to change strategy later

1. Go to secrets page
2. Click on the secret name (e.g., `FILTER_MIN_LP_LOCKED`)
3. Click "Update secret"
4. Enter new value
5. Save
6. Next workflow run will use new value

---

**You're all set!** Your strategy is now private and configurable.

See [docs/MAKE_REPO_PUBLIC_CHECKLIST.md](docs/MAKE_REPO_PUBLIC_CHECKLIST.md) for full details.
