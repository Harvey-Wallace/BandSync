#!/bin/bash

echo "🚀 Railway Deployment with Organization Migration"
echo "=================================================="

# Check if we're in Railway environment
if [ -z "$RAILWAY_ENVIRONMENT" ]; then
    echo "⚠️  Not in Railway environment, skipping migration"
    exit 0
fi

# Run the migration
echo "🔄 Running organization migration..."
python3 railway_migration.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

echo "🎉 Ready to deploy!"
