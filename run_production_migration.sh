#!/bin/bash

# Production Database Migration Script
# Runs the subscription tables migration on Railway production database

echo "🚀 Railway Production Migration"
echo "================================"

echo "📋 Step 1: Login to your BandSync production app"
echo "Go to: https://app.bandsync.co.uk/login"
echo "Login with your super admin account (Harvey258)"

echo ""
echo "📋 Step 2: Run migration via API"
echo "Make a POST request to:"
echo "URL: https://app.bandsync.co.uk/api/migration/run-subscription-migration"
echo "Headers:"
echo "  Authorization: Bearer <your-jwt-token>"
echo "  Content-Type: application/json"

echo ""
echo "📋 Step 3: Verify tables created"
echo "Make a GET request to:"
echo "URL: https://app.bandsync.co.uk/api/migration/check-subscription-tables"
echo "Headers:"
echo "  Authorization: Bearer <your-jwt-token>"

echo ""
echo "🔧 Alternative: Use browser console"
echo "1. Open browser dev tools on https://app.bandsync.co.uk"
echo "2. Run this JavaScript:"
echo ""
echo "// Get current token"
echo "const token = localStorage.getItem('token');"
echo ""
echo "// Run migration"
echo "fetch('/api/migration/run-subscription-migration', {"
echo "  method: 'POST',"
echo "  headers: {"
echo "    'Authorization': 'Bearer ' + token,"
echo "    'Content-Type': 'application/json'"
echo "  }"
echo "}).then(r => r.json()).then(console.log);"
echo ""
echo "// Check tables"
echo "fetch('/api/migration/check-subscription-tables', {"
echo "  headers: {"
echo "    'Authorization': 'Bearer ' + token"
echo "  }"
echo "}).then(r => r.json()).then(console.log);"

echo ""
echo "✅ Once migration is complete, the subscription system will be fully active!"
