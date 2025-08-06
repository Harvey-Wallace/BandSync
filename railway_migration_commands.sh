#!/bin/bash

# Direct Railway Time Fields Migration
# This script connects to Railway PostgreSQL and runs the migration SQL directly

echo "🚀 Railway Direct Migration Script"
echo "=================================="
echo ""

echo "📋 Step 1: Ensure Railway CLI is installed and logged in"
echo "  npm install -g @railway/cli"
echo "  railway login"
echo ""

echo "📋 Step 2: Connect to your Railway project"
echo "  railway link"
echo ""

echo "📋 Step 3: Run the migration SQL directly"
echo "  railway run psql \$DATABASE_URL -f add_time_fields_migration.sql"
echo ""

echo "📋 Alternative Step 3: Run using Python migration script"
echo "  railway run python3 railway_time_fields_migration.py"
echo ""

echo "🔧 Manual execution commands:"
echo "=================================="

# Direct SQL execution
echo ""
echo "Option A - Direct SQL:"
echo "railway run psql \$DATABASE_URL << 'EOF'"
cat add_time_fields_migration.sql
echo ""
echo "EOF"
echo ""

echo "Option B - Python script:"
echo "railway run python3 railway_time_fields_migration.py"
echo ""

echo "Option C - One-liner SQL:"
echo "railway run psql \$DATABASE_URL -c \"DO \\\$\\\$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'arrive_by_time') THEN ALTER TABLE event ADD COLUMN arrive_by_time TIME; END IF; IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'start_time') THEN ALTER TABLE event ADD COLUMN start_time TIME; END IF; IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'end_time') THEN ALTER TABLE event ADD COLUMN end_time TIME; END IF; END \\\$\\\$;\""
echo ""

echo "🔍 Verification command:"
echo "railway run psql \$DATABASE_URL -c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'event' AND column_name IN ('arrive_by_time', 'start_time', 'end_time') ORDER BY column_name;\""
echo ""

echo "📝 After migration succeeds:"
echo "1. Uncomment the time fields in backend/models.py"
echo "2. Deploy your application: railway up"
echo "3. Your timing features will now work!"
echo ""
