#!/bin/bash

# Build script for Railway deployment

set -e

echo "🏗️  Building BandSync for Railway..."

# Build the frontend
echo "📦 Building React frontend..."
cd frontend
npm install
npm run build

# Copy built files to backend static directory
echo "📁 Copying frontend build to backend..."
rm -rf ../backend/static
cp -r build ../backend/static

cd ..

echo "✅ Build completed successfully!"
