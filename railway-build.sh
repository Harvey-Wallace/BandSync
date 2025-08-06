#!/bin/bash
# Custom build script for Railway to pass environment variables to Docker build

echo "🚀 Starting custom Railway build..."
echo "📦 Building Docker image with environment variables..."

# Build with environment variables as build arguments
docker build \
  --build-arg REACT_APP_GOOGLE_MAPS_API_KEY="$REACT_APP_GOOGLE_MAPS_API_KEY" \
  --build-arg REACT_APP_API_URL="$REACT_APP_API_URL" \
  -t bandsync-app .

echo "✅ Build completed successfully!"
