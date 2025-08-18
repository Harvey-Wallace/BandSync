#!/bin/bash

echo "🚀 Starting Railway deployment with migrations..."

# Run database migrations
echo "🔧 Running database migrations..."
python3 migrations/add_magic_link_fields.py

# Start the application
echo "🎵 Starting BandSync application..."
exec "$@"
