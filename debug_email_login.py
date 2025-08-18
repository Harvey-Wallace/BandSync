#!/usr/bin/env python3
"""
Debug email login functionality
Check if email login is working correctly
"""

import requests
import sys

def test_email_login():
    """Test email login functionality"""
    
    print("🔍 Debugging Email Login Functionality")
    print("=" * 50)
    
    # Test with your live Railway site
    api_url = "https://app.bandsync.co.uk/api"
    
    print(f"🌐 Testing against: {api_url}")
    
    # Test email that should exist (replace with your actual email)
    test_email = input("\n📧 Enter your email address: ").strip()
    test_password = input("🔑 Enter your password: ").strip()
    
    if not test_email or not test_password:
        print("❌ Email and password required")
        return
    
    print(f"\n🧪 Testing email login...")
    print(f"   Email: {test_email}")
    print(f"   Password: {'*' * len(test_password)}")
    
    # Test 1: Email login
    print("\n1️⃣ Testing Email Login:")
    try:
        response = requests.post(f"{api_url}/auth/login", 
                               json={"email": test_email, "password": test_password}, 
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Email login SUCCESS!")
            print(f"   Role: {result.get('role', 'Unknown')}")
            print(f"   Organization: {result.get('organization', 'Unknown')}")
            return True
        else:
            try:
                error = response.json()
                print(f"   ❌ Email login FAILED: {error.get('msg', 'Unknown error')}")
            except:
                print(f"   ❌ Email login FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Email login ERROR: {e}")
    
    # Test 2: Try to find user by email (if you have access)
    print("\n2️⃣ Testing if email exists in database:")
    try:
        # This will fail but might give us info about the email
        response = requests.post(f"{api_url}/auth/password-reset-request", 
                               json={"email": test_email}, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Email found: {result.get('msg', 'Success')}")
        else:
            print(f"   ⚠️  Email test: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Email check ERROR: {e}")
    
    # Test 3: Compare with username login
    username = input(f"\n👤 Enter your username (for comparison): ").strip()
    if username:
        print("\n3️⃣ Testing Username Login (for comparison):")
        try:
            response = requests.post(f"{api_url}/auth/login", 
                                   json={"username": username, "password": test_password}, 
                                   timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Username login SUCCESS!")
                print(f"   Role: {result.get('role', 'Unknown')}")
                print(f"   Organization: {result.get('organization', 'Unknown')}")
            else:
                try:
                    error = response.json()
                    print(f"   ❌ Username login FAILED: {error.get('msg', 'Unknown error')}")
                except:
                    print(f"   ❌ Username login FAILED: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Username login ERROR: {e}")
    
    return False

def check_database_email():
    """Check what email is stored in the database"""
    print("\n📊 Database Email Check:")
    print("Let's run a quick query to see what email is stored...")
    
    db_url = input("🔗 Paste your Railway DATABASE_URL (if you want to check): ").strip()
    
    if db_url and 'rlwy.net' in db_url:
        try:
            import psycopg2
            
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            # Check what emails exist
            cur.execute("""
                SELECT username, email 
                FROM "user" 
                ORDER BY id;
            """)
            
            users = cur.fetchall()
            print("\n📋 Users in database:")
            for username, email in users:
                print(f"   - {username}: {email or 'NO EMAIL'}")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")
    else:
        print("   ⏭️  Skipping database check")

if __name__ == "__main__":
    print("🎵 BandSync Email Login Debug Tool")
    print("=" * 60)
    
    success = test_email_login()
    
    if not success:
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if your email is correctly stored in the database")
        print("2. Verify the password is correct")
        print("3. Make sure the latest code is deployed")
        print("4. Check Railway deployment logs")
        
        check_database_email()
    
    print("\n💡 Next steps:")
    print("1. Try username login to confirm password works")
    print("2. Check if email field is populated in database")
    print("3. Verify Railway deployment completed successfully")
