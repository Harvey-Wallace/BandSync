"""
Diagnose Railway database and email issues
Run this locally to test production database connection
"""

import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

def test_production_database():
    """Test connection to production database and check schema"""
    
    # Use Railway DATABASE_URL if available
    database_url = os.getenv('DATABASE_URL') or input("Enter Railway DATABASE_URL: ")
    
    if not database_url:
        print("❌ No DATABASE_URL provided")
        return False
    
    print(f"🔗 Testing connection to: {urlparse(database_url).hostname}")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check if user table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'user';
            """))
            
            if result.fetchone():
                print("✅ User table exists")
            else:
                print("❌ User table not found")
                return False
            
            # Check user table columns
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                ORDER BY column_name;
            """))
            
            columns = list(result.fetchall())
            print(f"✅ User table has {len(columns)} columns:")
            
            password_reset_columns = []
            for col_name, data_type in columns:
                if 'password_reset' in col_name:
                    password_reset_columns.append(col_name)
                    print(f"   🔐 {col_name}: {data_type}")
                elif col_name in ['username', 'email', 'password_hash']:
                    print(f"   👤 {col_name}: {data_type}")
            
            if not password_reset_columns:
                print("❌ Password reset columns missing!")
                print("   Need to run: ALTER TABLE \"user\" ADD COLUMN password_reset_token VARCHAR(255) NULL;")
                print("   Need to run: ALTER TABLE \"user\" ADD COLUMN password_reset_expires TIMESTAMP NULL;")
                return False
            
            # Check if users exist
            result = conn.execute(text("SELECT COUNT(*) FROM \"user\";"))
            user_count = result.fetchone()[0]
            print(f"✅ Found {user_count} users in database")
            
            if user_count == 0:
                print("❌ No users found - this might explain login issues")
                return False
            
            # Check specific user
            result = conn.execute(text("""
                SELECT username, email, password_hash IS NOT NULL as has_password
                FROM "user" 
                WHERE email = 'rob@harvey-wallace.co.uk' 
                OR username LIKE '%rob%' 
                LIMIT 5;
            """))
            
            users = list(result.fetchall())
            if users:
                print("✅ Found matching users:")
                for username, email, has_password in users:
                    print(f"   - {username} ({email}) - Password: {'✅' if has_password else '❌'}")
            else:
                print("❌ No matching users found")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_email_configuration():
    """Test email service configuration"""
    
    print("\n📧 Testing Email Configuration")
    print("=" * 40)
    
    required_vars = ['RESEND_API_KEY', 'FROM_EMAIL', 'FROM_NAME', 'BASE_URL']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'RESEND_API_KEY':
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Test Resend API key
    resend_key = os.getenv('RESEND_API_KEY')
    if resend_key:
        try:
            import requests
            response = requests.get(
                'https://api.resend.com/domains',
                headers={'Authorization': f'Bearer {resend_key}'}
            )
            if response.status_code == 200:
                print("✅ Resend API key is valid")
                domains = response.json()
                print(f"✅ Found {len(domains)} verified domains")
            else:
                print(f"❌ Resend API key test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to test Resend API: {e}")

if __name__ == "__main__":
    print("🔍 Railway Production Database Diagnosis")
    print("=" * 50)
    
    db_ok = test_production_database()
    test_email_configuration()
    
    print("\n📋 SUMMARY")
    print("=" * 20)
    
    if db_ok:
        print("✅ Database connection and schema look good")
    else:
        print("❌ Database issues found - check Railway database configuration")
    
    print("\n🔧 NEXT STEPS:")
    print("- If users are missing: Check if Railway is using the correct database")
    print("- If password reset columns are missing: Run the migration script")
    print("- If email variables are missing: Update Railway environment variables")
