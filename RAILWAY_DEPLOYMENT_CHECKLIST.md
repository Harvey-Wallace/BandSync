# Railway Deployment Checklist - Password Reset & Email Migration

## Pre-Deployment Checklist

### 1. Environment Variables
Verify these are set in Railway dashboard:

**Required for Backend:**
- [ ] `DATABASE_URL` (automatically set by Railway)
- [ ] `RESEND_API_KEY` (your Resend API key)
- [ ] `FROM_EMAIL` (e.g., noreply@bandsync.co.uk)
- [ ] `BASE_URL` (e.g., https://your-app.railway.app)
- [ ] `JWT_SECRET_KEY` (secure random string)
- [ ] `ENVIRONMENT=production`

**Required for Frontend (build-time):**
- [ ] `REACT_APP_API_URL` (e.g., https://your-app.railway.app/api)
- [ ] `REACT_APP_GOOGLE_MAPS_API_KEY` (your Google Maps API key)

**Required for Cloudinary:**
- [ ] `CLOUDINARY_CLOUD_NAME`
- [ ] `CLOUDINARY_API_KEY`
- [ ] `CLOUDINARY_API_SECRET`

### 2. Code Status
- [ ] All changes committed to git
- [ ] Frontend built and copied to backend/static
- [ ] Auto-migration code present in backend/app.py
- [ ] Password reset routes implemented
- [ ] Email service migrated to Resend

## Deployment Options

### Option 1: Automatic Migration (Recommended)
The migration runs automatically when the app starts up. Simply deploy:

```bash
# Build frontend
cd frontend
npm run build
cp -r build ../backend/static

# Deploy to Railway
railway up
```

### Option 2: Manual Migration
If you prefer to run the migration manually:

```bash
# Run the migration script
python run_railway_migration.py

# Then deploy
railway up
```

### Option 3: Full Deployment Script
Use the comprehensive deployment script:

```bash
python deploy_railway_with_migration.py
```

## Post-Deployment Verification

### 1. Check Deployment Logs
```bash
railway logs
```

Look for:
- ✅ "Password reset migration completed"
- ✅ "Database tables created successfully!"
- ✅ "BandSync Flask app is starting..."

### 2. Test Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "database": "connected",
  "migration": "completed"
}
```

### 3. Test API Routes
```bash
curl https://your-app.railway.app/debug/routes
```

Should return list of registered routes.

### 4. Test Password Reset Flow

**Request Password Reset:**
```bash
curl -X POST https://your-app.railway.app/api/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Check Frontend:**
- Visit: https://your-app.railway.app/login
- Click "Forgot Password?"
- Enter email and submit
- Check email for reset link

## Troubleshooting

### Migration Issues

**Problem:** Migration fails with "column already exists"
**Solution:** This is normal - the migration is idempotent and safe to run multiple times.

**Problem:** Database connection error
**Solution:** 
1. Check DATABASE_URL in Railway dashboard
2. Verify database service is running
3. Check Railway logs for connection errors

**Problem:** Permission denied
**Solution:** 
1. Verify database user has ALTER permissions
2. Check if DATABASE_URL is correctly formatted
3. Try restarting the Railway service

### Email Issues

**Problem:** Password reset emails not sending
**Solution:**
1. Verify RESEND_API_KEY is set
2. Check FROM_EMAIL domain is verified in Resend
3. Check Railway logs for email errors
4. Test email service: `python test_resend_email.py`

**Problem:** Email links not working
**Solution:**
1. Verify BASE_URL is correctly set
2. Check frontend routing for `/reset-password`
3. Verify token generation and validation

### Frontend Issues

**Problem:** Frontend not loading
**Solution:**
1. Check if build files are in backend/static
2. Verify frontend build completed successfully
3. Check for missing environment variables

**Problem:** API calls failing
**Solution:**
1. Verify REACT_APP_API_URL is set correctly
2. Check CORS configuration
3. Verify API routes are registered

## Emergency Procedures

### Disable Password Reset (if needed)
If password reset is causing issues:

```bash
python emergency_fix.py
```

This will:
- Comment out password reset routes
- Disable password reset UI
- Allow app to function without password reset

### Rollback Database
If migration causes issues:

```bash
railway run python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE user DROP COLUMN IF EXISTS password_reset_token'))
    conn.execute(text('ALTER TABLE user DROP COLUMN IF EXISTS password_reset_expires'))
    conn.commit()
    print('Password reset columns removed')
"
```

## Success Criteria

✅ **Deployment Successful When:**
- [ ] App starts without errors
- [ ] Database migration completes
- [ ] Health check returns "healthy"
- [ ] Login/logout works
- [ ] Password reset emails send
- [ ] Password reset links work
- [ ] All existing functionality preserved

## Support Resources

- **Railway Logs:** `railway logs`
- **Railway Status:** `railway status`
- **Railway Dashboard:** https://railway.app/dashboard
- **Resend Dashboard:** https://resend.com/dashboard
- **Test Scripts:** `test_resend_email.py`, `test_complete_flow.py`
1. Run environment variable checks
2. Install frontend dependencies
3. Build the React app (environment variables are compiled into the build)
4. Copy built files to backend static directory
5. Install backend dependencies
6. Start the Flask application

## Important Notes

- React environment variables are compiled into the build at build time
- Changes to `REACT_APP_*` variables require a rebuild
- The `.env` file is only used for local development
- Production environment variables must be set in Railway dashboard
