#!/bin/bash

echo "🔍 Testing Super Admin Analytics Endpoint Availability"
echo "Base URL: https://bandsync-production.up.railway.app/api"

echo ""
echo "1. Testing basic super-admin endpoint:"
curl -s -w "Status: %{http_code}\n" https://bandsync-production.up.railway.app/api/super-admin/overview -H "Authorization: Bearer dummy" | grep -E "(Status:|msg)"

echo ""
echo "2. Testing new analytics overview endpoint:"
curl -s -w "Status: %{http_code}\n" https://bandsync-production.up.railway.app/api/super-admin/analytics/overview -H "Authorization: Bearer dummy" | head -3

echo ""
echo "3. Testing if endpoint exists (should get 401/403, not 404):"
curl -s -w "Status: %{http_code}\n" -I https://bandsync-production.up.railway.app/api/super-admin/analytics/overview | grep "HTTP\|Status"

echo ""
echo "4. Testing alternative path:"
curl -s -w "Status: %{http_code}\n" https://bandsync-production.up.railway.app/api/super-admin/analytics -H "Authorization: Bearer dummy" | head -2

echo ""
echo "✅ Endpoint availability test complete"
