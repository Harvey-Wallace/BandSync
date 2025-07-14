# 🚨 RAILWAY DEPLOYMENT ISSUE RESOLUTION

## **ROOT CAUSE**
The password reset feature works locally but fails on Railway because:

1. **Database Migration Missing**: Production PostgreSQL database doesn't have password reset fields
2. **Environment Variables**: May need to be updated in Railway dashboard
3. **BASE_URL Configuration**: Had trailing slash (now fixed)

## **IMMEDIATE ACTIONS NEEDED**

### 1. **Update Railway Environment Variables**
Go to Railway dashboard → Variables tab → Add/Update:

```
RESEND_API_KEY=re_F2Q9H9qQ_G5EMpEAXRWCKKZGfG5pJvPbn
FROM_EMAIL=noreply@bandsync.co.uk
FROM_NAME=BandSync
BASE_URL=https://bandsync-production.up.railway.app
```

### 2. **Run Database Migration**
The production database needs these fields added:

**Option A: Manual SQL (Railway Console)**
```sql
ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL;
ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL;
```

**Option B: Use Migration Script**
Upload `railway_migrate_password_reset.py` and run it once on Railway.

### 3. **Deploy Code**
Push your latest changes to trigger Railway deployment.

### 4. **Test Production**
After deployment, test the endpoint:
```bash
curl -X POST https://bandsync-production.up.railway.app/api/auth/password-reset-request \
  -H "Content-Type: application/json" \
  -d '{"email": "rob@harvey-wallace.co.uk"}'
```

## **VERIFICATION CHECKLIST**

- [ ] Environment variables updated in Railway
- [ ] Database migration completed
- [ ] Code deployed to Railway
- [ ] Password reset request endpoint responds
- [ ] Email sent successfully
- [ ] Reset link works
- [ ] Password can be reset

## **EXPECTED RESPONSE**
Working endpoint should return:
```json
{"msg": "If an account with that email exists, a password reset link has been sent."}
```

## **DEBUGGING COMMANDS**

```bash
# Check Railway logs
railway logs

# Test endpoint
curl -X POST https://bandsync-production.up.railway.app/api/auth/password-reset-request \
  -H "Content-Type: application/json" \
  -d '{"email": "rob@harvey-wallace.co.uk"}'

# Check Railway variables
railway variables
```

## **MOST LIKELY ISSUE**
The **database migration** is the most likely culprit. Railway's PostgreSQL database doesn't have the password reset fields that were added to your local SQLite database.

**Solution**: Run the database migration on Railway first, then test the password reset functionality.

---

📋 **Files Created for Railway Deployment:**
- `railway_env_setup.sh` - Environment variables setup
- `railway_migrate_password_reset.py` - Database migration script
- `RAILWAY_PASSWORD_RESET_DEPLOYMENT.md` - Detailed deployment guide

🎯 **Next Step**: Run the database migration on Railway, then test the password reset flow!
