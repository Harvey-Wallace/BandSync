#!/usr/bin/env python3
"""
Check Railway environment variables for BandSync deployment
"""
import os

REQUIRED_VARS = {
    'DATABASE_URL': 'PostgreSQL connection string (auto-provided by Railway)',
    'JWT_SECRET': 'Secret key for JWT token generation',
    'CLOUDINARY_CLOUD_NAME': 'Cloudinary cloud name for image uploads',
    'CLOUDINARY_API_KEY': 'Cloudinary API key',
    'CLOUDINARY_API_SECRET': 'Cloudinary API secret',
}

OPTIONAL_VARS = {
    'GOOGLE_MAPS_API_KEY': 'Google Maps API key for location features',
    'SMTP_HOST': 'SMTP server host for email',
    'SMTP_PORT': 'SMTP server port (usually 587)',
    'SMTP_USER': 'SMTP username/email',
    'SMTP_PASS': 'SMTP password',
    'EMAIL_FROM': 'From email address',
    'FLASK_ENV': 'Flask environment (production)',
    'SECRET_KEY': 'Flask secret key',
}

def check_environment():
    print("🔍 Checking Railway Environment Variables for BandSync")
    print("=" * 60)
    
    print("\n✅ REQUIRED VARIABLES:")
    missing_required = []
    for var, description in REQUIRED_VARS.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * min(len(value), 20)} (set)")
        else:
            print(f"✗ {var}: MISSING - {description}")
            missing_required.append(var)
    
    print("\n📋 OPTIONAL VARIABLES:")
    missing_optional = []
    for var, description in OPTIONAL_VARS.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * min(len(value), 20)} (set)")
        else:
            print(f"- {var}: not set - {description}")
            missing_optional.append(var)
    
    print("\n" + "=" * 60)
    if missing_required:
        print(f"❌ MISSING {len(missing_required)} REQUIRED VARIABLES:")
        for var in missing_required:
            print(f"   - {var}")
        print("\n🚨 Your app may not work without these!")
    else:
        print("✅ All required variables are set!")
    
    if missing_optional:
        print(f"\n💡 {len(missing_optional)} optional variables not set (features may be limited)")
    
    print("\n🔧 To add variables in Railway:")
    print("1. Go to your Railway project dashboard")
    print("2. Click on your backend service")
    print("3. Go to 'Variables' tab")
    print("4. Click 'New Variable' and add each missing variable")

if __name__ == "__main__":
    check_environment()
