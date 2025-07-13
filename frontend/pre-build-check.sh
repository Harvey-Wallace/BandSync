#!/bin/bash

# Pre-build check script for environment variables
echo "🔍 Checking environment variables..."

# Check if critical environment variables are set
if [ -z "$REACT_APP_GOOGLE_MAPS_API_KEY" ]; then
    echo "⚠️  WARNING: REACT_APP_GOOGLE_MAPS_API_KEY is not set"
    echo "   Google Maps features will not work in the built application"
    echo "   Set this variable in Railway dashboard before deploying"
else
    echo "✅ REACT_APP_GOOGLE_MAPS_API_KEY is set"
fi

if [ -z "$REACT_APP_API_URL" ]; then
    echo "⚠️  WARNING: REACT_APP_API_URL is not set"
else
    echo "✅ REACT_APP_API_URL is set"
fi

echo "🏗️  Proceeding with build..."
