#!/bin/bash
# Test script for BandSync Navbar functionality

echo "🧪 Testing BandSync Navbar Functionality"
echo "======================================="

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the BandSync root directory"
    exit 1
fi

# Check environment variables
echo "🔍 Checking Environment Variables..."
echo "NODE_ENV: ${NODE_ENV:-'not set'}"
echo "REACT_APP_API_URL: ${REACT_APP_API_URL:-'not set'}"
echo "CLOUDINARY_CLOUD_NAME: ${CLOUDINARY_CLOUD_NAME:-'not set'}"

if [ -z "$REACT_APP_API_URL" ]; then
    echo "⚠️  WARNING: REACT_APP_API_URL not set!"
    echo "   This will cause navbar issues in production"
    echo "   Set this in Railway dashboard before deploying"
fi

# Test API endpoints
echo ""
echo "🌐 Testing API Endpoints..."

if [ ! -z "$REACT_APP_API_URL" ]; then
    echo "Testing: $REACT_APP_API_URL/api/auth/profile"
    curl -s -o /dev/null -w "%{http_code}" "$REACT_APP_API_URL/api/auth/profile" || echo "❌ Auth profile endpoint unreachable"
    
    echo "Testing: $REACT_APP_API_URL/api/admin/organization"
    curl -s -o /dev/null -w "%{http_code}" "$REACT_APP_API_URL/api/admin/organization" || echo "❌ Admin organization endpoint unreachable"
    
    echo "Testing: $REACT_APP_API_URL/api/organizations/current"
    curl -s -o /dev/null -w "%{http_code}" "$REACT_APP_API_URL/api/organizations/current" || echo "❌ Organizations current endpoint unreachable"
else
    echo "⚠️  Skipping API tests - REACT_APP_API_URL not set"
fi

# Check frontend files
echo ""
echo "📁 Checking Frontend Files..."

if [ -f "frontend/src/components/Navbar.js" ]; then
    echo "✅ Navbar.js exists"
    
    # Check for API URL usage
    if grep -q "REACT_APP_API_URL" "frontend/src/components/Navbar.js"; then
        echo "✅ Navbar.js uses REACT_APP_API_URL"
    else
        echo "❌ Navbar.js missing REACT_APP_API_URL"
    fi
else
    echo "❌ Navbar.js not found"
fi

if [ -f "frontend/src/contexts/ThemeContext.js" ]; then
    echo "✅ ThemeContext.js exists"
    
    # Check for API URL usage
    if grep -q "REACT_APP_API_URL" "frontend/src/contexts/ThemeContext.js"; then
        echo "✅ ThemeContext.js uses REACT_APP_API_URL"
    else
        echo "❌ ThemeContext.js missing REACT_APP_API_URL"
    fi
else
    echo "❌ ThemeContext.js not found"
fi

# Check backend routes
echo ""
echo "🔧 Checking Backend Routes..."

if [ -f "backend/routes/admin.py" ]; then
    echo "✅ Admin routes exist"
    
    if grep -q "@admin_bp.route('/organization'" "backend/routes/admin.py"; then
        echo "✅ Admin organization route exists"
    else
        echo "❌ Admin organization route missing"
    fi
else
    echo "❌ Admin routes not found"
fi

if [ -f "backend/routes/organizations.py" ]; then
    echo "✅ Organization routes exist"
    
    if grep -q "@org_bp.route('/current'" "backend/routes/organizations.py"; then
        echo "✅ Organization current route exists"
    else
        echo "❌ Organization current route missing"
    fi
else
    echo "❌ Organization routes not found"
fi

# Check for common issues
echo ""
echo "🔍 Checking for Common Issues..."

# Check for hardcoded URLs
if grep -r "localhost:5000" frontend/src/ 2>/dev/null; then
    echo "❌ Found hardcoded localhost URLs in frontend"
else
    echo "✅ No hardcoded localhost URLs found"
fi

# Check for missing fallback
if grep -r "REACT_APP_API_URL ||" frontend/src/ 2>/dev/null; then
    echo "✅ Found API URL fallback patterns"
else
    echo "❌ Missing API URL fallback patterns"
fi

echo ""
echo "📋 Summary:"
echo "=========="
echo "1. Set REACT_APP_API_URL in Railway dashboard"
echo "2. Ensure it matches your Railway app domain"
echo "3. Redeploy after setting environment variables"
echo "4. Test navbar functionality after deployment"
echo ""
echo "Example Railway domain: https://bandsync-production.up.railway.app"
echo "Set as: REACT_APP_API_URL=https://bandsync-production.up.railway.app"
