# Railway Deployment with Magic Link Migration

## Quick Setup Commands

### 1. Install Railway CLI (if not already installed)
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Connect to your project
```bash
railway link
```

### 4. Run migration on Railway database
```bash
railway run python3 railway_magic_link_migration.py
```

### 5. Deploy your changes
```bash
railway up
```

## Alternative: Direct SQL Migration

### Via Railway Dashboard
1. Go to Railway → Your Project → PostgreSQL
2. Click "Data" or "Connect" 
3. Run this SQL:

```sql
-- Add magic link fields (safe to run multiple times)
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS magic_link_token VARCHAR(255);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS magic_link_expires TIMESTAMP;
```

### Via Railway CLI
```bash
# Connect to Railway database and run SQL
railway connect postgresql < add_magic_link_fields.sql
```

## Automatic Migration on Deploy

### Option 1: Update Railway Start Command
In Railway dashboard, change your start command to:
```bash
python3 railway_magic_link_migration.py && python app.py
```

### Option 2: Add to Procfile (if using)
```
release: python3 railway_magic_link_migration.py
web: python app.py
```

### Option 3: Add to Railway Build Process
In railway.toml:
```toml
[build]
builder = "NIXPACKS"

[build.nixpacksConfigOverride]
phases.setup.nixpkgs = ["python3", "postgresql"]
phases.install.cmds = ["pip install -r requirements.txt"]
phases.build.cmds = ["python3 railway_magic_link_migration.py"]

[deploy]
startCommand = "python app.py"
```

## Verification

After deployment, test the new features:

1. **Email Login**: Try logging in with email instead of username
2. **Magic Link**: Click "Login with email link" and check email
3. **Database**: Verify columns exist:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name='user' AND column_name LIKE 'magic_link%';
   ```

## Troubleshooting

### If migration fails on Railway:
1. Check Railway logs: `railway logs`
2. Manually run SQL in Railway dashboard
3. Verify DATABASE_URL environment variable
4. Check database connectivity

### If features don't work after deploy:
1. Verify migration completed successfully
2. Check that email service is configured on Railway
3. Test magic link endpoints via Railway domain
4. Review Railway application logs
