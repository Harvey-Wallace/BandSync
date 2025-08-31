#!/usr/bin/env python3
"""
Stripe Configuration Checker
Verifies that Stripe keys are properly configured in the environment
"""

import os
import requests
import logging

def check_stripe_configuration():
    """Check if Stripe is properly configured"""
    
    print("🔍 Checking Stripe Configuration...")
    print("=" * 50)
    
    # Check environment variables
    stripe_public_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
    stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    print(f"✅ STRIPE_PUBLISHABLE_KEY: {'Set' if stripe_public_key else '❌ Missing'}")
    print(f"✅ STRIPE_SECRET_KEY: {'Set (hidden)' if stripe_secret_key else '❌ Missing'}")
    print(f"✅ STRIPE_WEBHOOK_SECRET: {'Set (hidden)' if stripe_webhook_secret else '❌ Missing'}")
    
    if not stripe_public_key:
        print("\n⚠️  Add this to Railway environment variables:")
        print("STRIPE_PUBLISHABLE_KEY=pk_test_...")
        
    if not stripe_secret_key:
        print("\n⚠️  Add this to Railway environment variables:")
        print("STRIPE_SECRET_KEY=sk_test_...")
        
    if not stripe_webhook_secret:
        print("\n⚠️  Add this to Railway environment variables:")
        print("STRIPE_WEBHOOK_SECRET=whsec_...")
    
    # Test API connectivity
    if stripe_secret_key:
        try:
            import stripe
            stripe.api_key = stripe_secret_key
            
            # Test API call
            customers = stripe.Customer.list(limit=1)
            print(f"\n✅ Stripe API Connection: Working")
            
        except Exception as e:
            print(f"\n❌ Stripe API Connection: Failed ({str(e)})")
    
    print("\n" + "=" * 50)
    print("🔗 Next steps:")
    print("1. Get keys from: https://dashboard.stripe.com/test/apikeys")
    print("2. Add to Railway: railway variables set STRIPE_PUBLISHABLE_KEY=pk_test_...")
    print("3. Set up webhook endpoint: https://app.bandsync.co.uk/api/subscription/webhook")

if __name__ == "__main__":
    check_stripe_configuration()
