#!/bin/bash

# Quick Production Setup for BandSync Payment System
# Run this after getting Stripe test keys

echo "🚀 BandSync Payment System - Quick Setup"
echo "========================================"

echo ""
echo "📋 Required Stripe Keys (get from https://dashboard.stripe.com/test/apikeys):"
echo "1. Publishable Key (starts with pk_test_)"
echo "2. Secret Key (starts with sk_test_)"
echo "3. Webhook Secret (starts with whsec_) - get after setting up webhook"

echo ""
echo "🔧 Railway Environment Setup:"
echo "Run these commands in your terminal (replace with actual keys):"
echo ""
echo "railway login"
echo "railway link"  # Link to BandSync project
echo "railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here"
echo "railway variables set STRIPE_SECRET_KEY=sk_test_your_key_here"
echo "railway variables set STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here"

echo ""
echo "🔗 Stripe Webhook Setup:"
echo "1. Go to: https://dashboard.stripe.com/test/webhooks"
echo "2. Click 'Add endpoint'"
echo "3. URL: https://app.bandsync.co.uk/api/subscription/webhook"
echo "4. Select events:"
echo "   - customer.subscription.created"
echo "   - customer.subscription.updated"
echo "   - customer.subscription.deleted"
echo "   - payment_intent.succeeded"
echo "5. Copy the webhook signing secret to Railway"

echo ""
echo "🗄️ Database Migration:"
echo "After Railway redeploys with new environment variables:"
echo "1. Go to https://app.bandsync.co.uk"
echo "2. Login as super admin (Harvey258)"
echo "3. Open browser console (F12)"
echo "4. Run migration script:"
echo ""
echo "const token = localStorage.getItem('token');"
echo "fetch('/api/migration/run-subscription-migration', {"
echo "  method: 'POST',"
echo "  headers: {"
echo "    'Authorization': 'Bearer ' + token,"
echo "    'Content-Type': 'application/json'"
echo "  }"
echo "}).then(r => r.json()).then(console.log);"

echo ""
echo "✅ Test Payment:"
echo "1. Create a test organization"
echo "2. Click 'Subscription' in navigation"
echo "3. Click 'Upgrade to Pro'"
echo "4. Use test card: 4242 4242 4242 4242"
echo "5. Verify success page and unlimited users"

echo ""
echo "🎉 Once complete, your payment system will be fully operational!"
