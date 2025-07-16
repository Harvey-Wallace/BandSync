#!/bin/bash

echo "🚀 Railway Deployment with Database Migration"
echo "=============================================="

# Run the migration script
python3 deploy_with_migration.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

echo "🎉 Deployment setup complete!"
