#!/bin/bash

# Railway startup script with migration
# This script runs migrations before starting the Flask application

set -e  # Exit on any error

echo "🚀 BandSync Railway Deployment Starting..."
echo "Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Check if we're in Railway environment
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "✓ Running in Railway environment: $RAILWAY_ENVIRONMENT"
else
    echo "⚠️  Not detected as Railway environment"
fi

# Check database connectivity before migration
echo "🔍 Checking database connectivity..."
if [ -n "$DATABASE_URL" ]; then
    echo "✓ DATABASE_URL is configured"
else
    echo "❌ DATABASE_URL not found - checking individual variables..."
    if [ -n "$PGHOST" ] && [ -n "$PGDATABASE" ] && [ -n "$PGUSER" ]; then
        echo "✓ PostgreSQL environment variables found"
    else
        echo "❌ No database configuration found!"
        exit 1
    fi
fi

# Run database migration with timeout
echo "🔄 Running database migrations..."
timeout 60 python railway_rsvp_visibility_migration.py

migration_exit_code=$?
if [ $migration_exit_code -eq 0 ]; then
    echo "✅ Migration completed successfully"
elif [ $migration_exit_code -eq 124 ]; then
    echo "⚠️  Migration timed out after 60 seconds - proceeding with startup"
    echo "   (Migration may still be running or database may be slow)"
else
    echo "❌ Migration failed with exit code: $migration_exit_code"
    echo "🔄 Attempting to start application anyway..."
fi

# Wait a moment for any background processes to settle
sleep 2

# Start the Flask application
echo "🌟 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 120 app:app
