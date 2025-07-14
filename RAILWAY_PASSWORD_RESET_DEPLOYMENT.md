# Railway Password Reset Deployment Checklist

## 🚨 CRITICAL ISSUES TO CHECK

### 1. **Database Migration Required**
The production database needs the password reset fields added.

**Solution:** Run this migration on Railway:
```python
# Add to your Railway startup or run manually
ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL;
ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL;
```

### 2. **Environment Variables**
Check these are set in Railway dashboard:

**Backend Variables:**
- `RESEND_API_KEY` = `re_F2Q9H9qQ_G5EMpEAXRWCKKZGfG5pJvPbn`
- `FROM_EMAIL` = `noreply@bandsync.co.uk`
- `FROM_NAME` = `BandSync`
- `BASE_URL` = `https://bandsync-production.up.railway.app` (NO trailing slash)

**Frontend Variables:**
- `REACT_APP_API_URL` = `https://bandsync-production.up.railway.app`

### 3. **BASE_URL Configuration Issue**
The BASE_URL in your .env has a trailing slash, which could cause issues with password reset links.

**Current:** `https://bandsync-production.up.railway.app/`
**Should be:** `https://bandsync-production.up.railway.app`

### 4. **Import Path Issues**
The password reset routes import `EmailService` - ensure the import path is correct in production.

### 5. **Database Connection**
Railway uses PostgreSQL in production vs SQLite locally. The migration needs to be run on the production database.

## 🔧 **IMMEDIATE FIXES NEEDED**

### Fix 1: Update BASE_URL (Remove trailing slash)
In Railway dashboard, update:
- `BASE_URL` = `https://bandsync-production.up.railway.app`

### Fix 2: Database Migration
Run the migration script on Railway to add password reset fields.

### Fix 3: Test Email Service
Verify the email service is working in production:
```bash
# Test endpoint
curl -X POST https://bandsync-production.up.railway.app/api/auth/password-reset-request \
  -H "Content-Type: application/json" \
  -d '{"email": "rob@harvey-wallace.co.uk"}'
```

## 🐛 **COMMON DEPLOYMENT ERRORS**

1. **"Column does not exist"** - Database migration not run
2. **"Email service not configured"** - Missing RESEND_API_KEY
3. **"Invalid reset link"** - BASE_URL misconfiguration
4. **"Module not found"** - Import path issues
5. **"CORS errors"** - Frontend/backend URL mismatch

## 📋 **TESTING CHECKLIST**

After deploying:
- [ ] Database migration completed
- [ ] Environment variables updated
- [ ] Password reset request endpoint responds
- [ ] Email is sent successfully
- [ ] Reset link points to correct URL
- [ ] Password reset page loads
- [ ] Password reset completes successfully

## 🚀 **DEPLOYMENT STEPS**

1. **Update Environment Variables** in Railway dashboard
2. **Deploy code** (git push or Railway deploy)
3. **Run database migration** (manually or via Railway console)
4. **Test password reset flow** end-to-end
5. **Monitor Railway logs** for errors

## 🔍 **DEBUGGING COMMANDS**

Check Railway logs:
```bash
# View application logs
railway logs

# Check environment variables
railway variables

# Connect to database
railway connect
```

The most likely issue is the **database migration** - the production database doesn't have the password reset fields yet.
