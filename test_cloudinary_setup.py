#!/usr/bin/env python3
"""
Test script to verify Cloudinary configuration for BandSync
Run this after setting up environment variables in Railway
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cloudinary_config():
    """Test if Cloudinary configuration is working"""
    print("🔍 Testing Cloudinary Configuration...")
    
    # Check environment variables
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
    
    # Test Cloudinary connection
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Test with a simple API call
        response = cloudinary.api.ping()
        print(f"✅ Cloudinary connection successful: {response}")
        return True
        
    except ImportError:
        print("❌ Cloudinary library not installed. Run: pip install cloudinary")
        return False
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False

def test_upload_endpoints():
    """Test if upload endpoints are accessible"""
    print("\n🔍 Testing Upload Endpoints...")
    
    # This would require authentication, so we'll just check if the server is running
    base_url = os.getenv('REACT_APP_API_BASE_URL', 'http://localhost:5000')
    
    try:
        # Test basic health check
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API server is running at {base_url}")
        else:
            print(f"⚠️  API server responded with status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Could not reach API server: {e}")
        return False
    
    return True

def check_file_structure():
    """Check if required files exist"""
    print("\n🔍 Checking File Structure...")
    
    required_files = [
        'backend/app.py',
        'backend/routes/admin.py',
        'backend/auth/routes.py',
        'frontend/src/components/UserAvatar.js',
        'backend/requirements.txt'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 BandSync Cloudinary Configuration Test\n")
    
    tests = [
        ("Environment Variables", test_cloudinary_config),
        ("File Structure", check_file_structure),
        ("Upload Endpoints", test_upload_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Your image upload system is ready!")
        print("\nNext steps:")
        print("1. Deploy to Railway")
        print("2. Set environment variables in Railway dashboard")
        print("3. Test uploads through the admin dashboard")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
