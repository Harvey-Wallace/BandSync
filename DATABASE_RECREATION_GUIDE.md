# Railway Database Recreation Guide

## Step 1: Delete Current Database

1. **Open Railway Dashboard**
   - The dashboard should be open in your browser (we ran `railway open`)
   - Navigate to your BandSync project

2. **Delete Postgres Service**
   - Find the "Postgres" service in your project
   - Click on the Postgres service
   - Go to "Settings" tab
   - Scroll down to "Danger Zone"
   - Click "Delete Service"
   - Confirm the deletion

## Step 2: Create New Database

1. **Add New Database Service**
   - In your Railway project dashboard
   - Click "Add Service" or "+"
   - Select "Database" → "PostgreSQL"
   - Railway will provision a new Postgres database

2. **Wait for Deployment**
   - Wait for the new database to be fully deployed
   - The status should show as "Active"

## Step 3: Get New Database URL

1. **Get Connection Details**
   - Click on the new Postgres service
   - Go to "Variables" tab
   - Copy the `DATABASE_URL` value

2. **Update Environment**
   - The new DATABASE_URL will be automatically available to your BandSync service
   - You can verify this by checking the BandSync service variables

## Step 4: Setup Database Schema

1. **Run the Setup Script**
   ```bash
   cd /Users/robertharvey/Documents/GitHub/BandSync
   source backend/venv/bin/activate
   python setup_new_database.py
   ```

2. **When prompted, enter the new DATABASE_URL**

## Step 5: Update Local Environment

1. **Update backend/.env**
   ```bash
   cd backend
   # Update the DATABASE_URL in your .env file with the new connection string
   ```

2. **Test the Connection**
   ```bash
   python ../test_railway_database.py
   ```

## Step 6: Redeploy Application

1. **Redeploy BandSync Service**
   ```bash
   railway service BandSync
   railway redeploy
   ```

2. **Test Login**
   - Try logging in with Rob123 / Rob123pass
   - The credentials should work with the fresh database

## Alternative: Quick Database Reset

If you want to keep the same database but just reset the data:

```bash
# Connect to current database
railway connect

# Drop all tables (be careful!)
DROP TABLE IF EXISTS rsvp CASCADE;
DROP TABLE IF EXISTS event CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS organization CASCADE;

# Exit psql
\q

# Then run setup script with current DATABASE_URL
```

---

**Note**: The setup script will create:
- Organization table with "Test Band" organization
- User table with Rob123 user (password: Rob123pass)
- Event and RSVP tables
- All necessary relationships and constraints
