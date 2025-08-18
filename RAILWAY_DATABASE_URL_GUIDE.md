📋 **How to Get Your Railway EXTERNAL Database URL**

## 🎯 Step-by-Step Guide:

### Method 1: Railway Dashboard
1. **Go to**: [railway.app](https://railway.app)
2. **Click**: Your BandSync project
3. **Click**: Your PostgreSQL service
4. **Click**: "Connect" tab (or "Variables" tab)
5. **Look for**: "Public Networking" or "External Connection"
6. **Copy**: The URL that looks like:
   ```
   postgresql://postgres:PASSWORD@HOST.railway.app:PORT/railway
   ```
   
   **NOT the internal one** (postgres.railway.internal)

### Method 2: Railway CLI
```bash
railway login
railway link
railway variables
```
Look for `DATABASE_URL` in the output.

### Method 3: Environment Variables
In Railway dashboard:
1. Go to your **backend service** (not PostgreSQL)
2. Click "Variables" tab
3. Look for `DATABASE_URL`

## 🔍 What to Look For:

✅ **CORRECT External URL**:
```
postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@caboose.proxy.rlwy.net:46206/railway
```

❌ **WRONG Internal URL**:
```
postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@postgres.railway.internal:5432/railway
```

## 🔑 Key Differences:
- External: `something.railway.app` or `something.rlwy.net`
- Internal: `postgres.railway.internal` (only works inside Railway)

---

Once you have the correct external URL, run:
```bash
python3 railway_direct_migration.py
```
