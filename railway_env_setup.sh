#!/bin/bash

# Railway Environment Variables Setup Script
# Copy these values to your Railway dashboard under Variables tab

echo "🚀 Railway Environment Variables for Password Reset"
echo "=================================================="
echo ""
echo "📋 REQUIRED VARIABLES:"
echo ""
echo "RESEND_API_KEY=re_F2Q9H9qQ_G5EMpEAXRWCKKZGfG5pJvPbn"
echo "FROM_EMAIL=noreply@bandsync.co.uk"
echo "FROM_NAME=BandSync"
echo "BASE_URL=https://bandsync-production.up.railway.app"
echo ""
echo "📝 STEPS:"
echo "1. Go to your Railway project dashboard"
echo "2. Click on 'Variables' tab"
echo "3. Add/update the above variables"
echo "4. Deploy your app"
echo "5. Run database migration (see migration script)"
echo ""
echo "🔍 DEBUGGING:"
echo "- Check Railway logs: railway logs"
echo "- Test endpoint: curl -X POST https://bandsync-production.up.railway.app/api/auth/password-reset-request -H 'Content-Type: application/json' -d '{\"email\": \"rob@harvey-wallace.co.uk\"}'"
echo ""
