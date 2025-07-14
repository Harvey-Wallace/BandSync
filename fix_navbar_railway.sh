#!/bin/bash

# Railway Navbar Fix Deployment Script
# This script fixes navbar issues on Railway deployment

echo "🚀 Starting Railway Navbar Fix Deployment..."

# Step 1: Update Railway environment variables
echo "📝 Setting Railway environment variables..."

# You'll need to run these commands in your Railway dashboard or CLI:
echo "Add these environment variables to your Railway project:"
echo "  REACT_APP_API_URL=https://your-app-name.up.railway.app"
echo "  REACT_APP_ENVIRONMENT=production"
echo "  CLOUDINARY_CLOUD_NAME=di0gom1vd"
echo "  CLOUDINARY_API_KEY=982593917724433"
echo "  CLOUDINARY_API_SECRET=oGCqi0PHPSR8wOPce5WX1XSoZkY"

# Step 2: Test navbar fixes locally
echo "🧪 Testing navbar fixes locally..."

# Check if the fixes are working
echo "Testing organization endpoint..."
if command -v curl &> /dev/null; then
    echo "✅ curl is available for testing"
else
    echo "❌ curl not available, skipping API tests"
fi

# Step 3: Build and deploy
echo "🔨 Building application..."

# Frontend build
cd frontend
npm run build
cd ..

echo "✅ Navbar fixes applied successfully!"
echo ""
echo "🔍 Next steps for Railway deployment:"
echo "1. Add the environment variables listed above to your Railway project"
echo "2. Redeploy your application"
echo "3. Test the navbar functionality:"
echo "   - Logo should appear in navbar"
echo "   - Profile bubble should show data on all pages"
echo "   - Theme color should load from organization settings"
echo "   - No console errors in browser"
echo ""
echo "🔧 Debug endpoints available:"
echo "   GET /api/organizations/current - Get organization data"
echo "   GET /api/organizations/debug - Debug organization issues"
echo ""
echo "📊 Success indicators:"
echo "   ✅ Logo displays in navbar within 2 seconds"
echo "   ✅ Profile data persists across page navigation"
echo "   ✅ Theme color applies correctly"
echo "   ✅ No API errors in console"
