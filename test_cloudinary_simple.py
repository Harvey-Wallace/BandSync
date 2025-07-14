#!/usr/bin/env python3
"""
Simple test to verify Cloudinary is configured correctly
"""

import os

def test_cloudinary_basic():
    """Test basic Cloudinary configuration"""
    print("🔍 Testing Basic Cloudinary Configuration...")
    
    # Test environment variables
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not cloud_name:
        print("❌ CLOUDINARY_CLOUD_NAME not set")
        return False
    
    if not api_key:
        print("❌ CLOUDINARY_API_KEY not set")
        return False
    
    if not api_secret:
        print("❌ CLOUDINARY_API_SECRET not set")
        return False
    
    print(f"✅ Cloud Name: {cloud_name}")
    print(f"✅ API Key: {api_key[:6]}...{api_key[-4:]}")
    print(f"✅ API Secret: {'*' * len(api_secret)}")
    
    # Test Cloudinary library
    try:
        import cloudinary
        import cloudinary.api
        print("✅ Cloudinary library imported successfully")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        print("✅ Cloudinary configured successfully")
        
        # Test basic API call
        try:
            response = cloudinary.api.ping()
            print(f"✅ Cloudinary API connection successful: {response}")
            return True
        except Exception as e:
            print(f"❌ Cloudinary API connection failed: {e}")
            return False
        
    except ImportError:
        print("❌ Cloudinary library not installed")
        return False
    except Exception as e:
        print(f"❌ Cloudinary configuration failed: {e}")
        return False

def main():
    print("🚀 BandSync Cloudinary Test\n")
    
    if test_cloudinary_basic():
        print("\n🎉 Cloudinary is configured correctly!")
        print("\nYour image upload system is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Add these environment variables to Railway dashboard")
        print("2. Deploy to Railway")
        print("3. Test image uploads through the admin interface")
    else:
        print("\n❌ Cloudinary configuration failed")
        print("Please check your environment variables and try again")

if __name__ == "__main__":
    main()
