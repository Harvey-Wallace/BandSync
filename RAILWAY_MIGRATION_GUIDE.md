# 🚀 Railway Database Migration Guide

## **How to Run Password Reset Migration on Railway**

### **Method 1: Automatic Migration (Recommended)**

✅ **ALREADY IMPLEMENTED** - The migration will run automatically when you deploy!

The app will automatically add password reset fields on startup. Just deploy your latest code:

```bash
# Push to trigger Railway deployment
git push origin main
```

The migration runs in `app.py` and will:
- Check if password reset columns exist
- Add them if missing
- Log success/failure

### **Method 2: Railway Console**

If you want to run the migration manually:

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Login and Connect
```bash
railway login
railway link  # Select your BandSync project
```

#### Step 3: Run Migration Script
```bash
railway shell
cd /app
python migrate_password_reset_railway.py
```

### **Method 3: Railway Database Console**

#### Step 1: Connect to Database
```bash
railway connect
```

#### Step 2: Run SQL Commands
```sql
-- Check if columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name IN ('password_reset_token', 'password_reset_expires');

-- Add columns if missing
ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL;
ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL;
```

### **Method 4: One-time Migration Service**

Create a temporary migration service in Railway:

1. **Create new service** in your Railway project
2. **Upload migration script** as a simple service
3. **Run once** and then delete the service

## **Verification Steps**

### 1. Check Railway Logs
```bash
railway logs --tail 50
```

Look for:
- `✅ Added password_reset_token column`
- `✅ Added password_reset_expires column`
- `🎉 Password reset migration completed`

### 2. Test the Endpoints
```bash
# Test login (should work)
curl -X POST https://bandsync-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "rob@harvey-wallace.co.uk", "password": "yourpassword"}'

# Test password reset (should work after migration)
curl -X POST https://bandsync-production.up.railway.app/api/auth/password-reset-request \
  -H "Content-Type: application/json" \
  -d '{"email": "rob@harvey-wallace.co.uk"}'
```

### 3. Check Database Schema
```bash
railway connect
\d user  # PostgreSQL command to describe table
```

## **Expected Results**

### Before Migration:
```
❌ Password reset endpoints return 503 "temporarily unavailable"
❌ Login might fail due to database issues
```

### After Migration:
```
✅ Password reset request works
✅ Password reset emails sent
✅ Login functionality restored
✅ Database has password_reset_token and password_reset_expires columns
```

## **Troubleshooting**

### Migration Fails:
1. **Check DATABASE_URL** is set in Railway
2. **Check database permissions**
3. **Run manually** via Railway console
4. **Check logs** for specific error messages

### Still Not Working:
1. **Check environment variables** in Railway dashboard
2. **Verify email service** configuration
3. **Check Railway logs** for errors
4. **Test with health endpoint** (when it's deployed)

## **Current Status**

✅ **Auto-migration code added** to app.py
✅ **Safer error handling** implemented
✅ **Manual migration script** available
📋 **Next**: Deploy and verify migration runs successfully

## **Deploy Command**

```bash
# Commit and push (if not already done)
git add -A
git commit -m "Add auto-migration for password reset fields"
git push origin main

# Check Railway deployment
railway status
railway logs --tail 100
```

The migration will run automatically when Railway deploys your app!
