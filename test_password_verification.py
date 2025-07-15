#!/usr/bin/env python3
"""
Test password verification logic with actual database data
"""

import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

# Database connection
external_db_url = "postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@caboose.proxy.rlwy.net:46206/railway"

def test_password_verification():
    """Test password verification with actual database data"""
    try:
        print("🔍 Testing password verification...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Get the testuser data
        cur.execute("""
            SELECT id, username, email, password_hash
            FROM "user" 
            WHERE username = 'testuser'
            LIMIT 1;
        """)
        
        user_data = cur.fetchone()
        if not user_data:
            print("❌ testuser not found in database")
            return False
        
        user_id, username, email, password_hash = user_data
        print(f"✅ Found user: {username} ({email})")
        print(f"Password hash: {password_hash[:50]}...")
        
        # Test password verification
        test_password = "testpass"
        is_valid = check_password_hash(password_hash, test_password)
        print(f"Password verification result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        # Test creating a new hash for comparison
        new_hash = generate_password_hash(test_password)
        print(f"New hash for same password: {new_hash[:50]}...")
        
        # Test if new hash works
        new_hash_valid = check_password_hash(new_hash, test_password)
        print(f"New hash verification: {'✅ VALID' if new_hash_valid else '❌ INVALID'}")
        
        # If the original hash is invalid, let's update it
        if not is_valid:
            print("⚠️  Original hash is invalid, updating...")
            cur.execute("""
                UPDATE "user" 
                SET password_hash = %s 
                WHERE id = %s;
            """, (new_hash, user_id))
            conn.commit()
            print("✅ Password hash updated in database")
        
        conn.close()
        return is_valid
        
    except Exception as e:
        print(f"❌ Error testing password: {e}")
        return False

def test_other_users():
    """Test password verification for other users"""
    try:
        print("\n🔍 Testing other users...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Get all users
        cur.execute("""
            SELECT id, username, email, password_hash
            FROM "user" 
            ORDER BY id;
        """)
        
        users = cur.fetchall()
        for user_id, username, email, password_hash in users:
            print(f"\n👤 User: {username}")
            
            # Try common passwords
            test_passwords = ["testpass", "password", "123456", username]
            
            for test_pass in test_passwords:
                is_valid = check_password_hash(password_hash, test_pass)
                if is_valid:
                    print(f"  ✅ Password '{test_pass}' is VALID")
                    break
            else:
                print(f"  ❌ None of the test passwords worked")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing other users: {e}")

if __name__ == "__main__":
    print("🔧 BandSync Password Verification Test")
    print("=" * 50)
    
    # Test main user
    test_password_verification()
    
    # Test other users
    test_other_users()
    
    print("\n🎯 Next steps:")
    print("1. If passwords were updated, try logging in again")
    print("2. Check Railway logs for any login attempt details")
    print("3. Test with the frontend login form")
