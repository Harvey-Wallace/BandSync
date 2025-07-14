"""
Check if password reset fields exist in database
Run this to diagnose database issues
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_database_schema():
    """Check if password reset fields exist"""
    
    try:
        from app import app
        from models import db
        from sqlalchemy import text
        
        with app.app_context():
            print("🔍 Checking database schema for password reset fields...")
            
            # Check if columns exist
            result = db.engine.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
                ORDER BY column_name;
            """))
            
            columns = list(result.fetchall())
            
            if not columns:
                print("❌ Password reset fields NOT found in database")
                print("🔧 Need to run database migration:")
                print("   ALTER TABLE \"user\" ADD COLUMN password_reset_token VARCHAR(255) NULL;")
                print("   ALTER TABLE \"user\" ADD COLUMN password_reset_expires TIMESTAMP NULL;")
                return False
            else:
                print("✅ Password reset fields found:")
                for col_name, data_type in columns:
                    print(f"   - {col_name}: {data_type}")
                return True
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'RESEND_API_KEY',
        'FROM_EMAIL', 
        'FROM_NAME',
        'BASE_URL',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'RESEND_API_KEY':
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

if __name__ == "__main__":
    print("🔐 Password Reset Deployment Diagnosis")
    print("=" * 50)
    
    env_ok = check_environment_variables()
    db_ok = check_database_schema()
    
    print("\n📋 SUMMARY:")
    print("=" * 20)
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ MISSING'}")
    print(f"Database Schema: {'✅ OK' if db_ok else '❌ MISSING'}")
    
    if env_ok and db_ok:
        print("\n🎉 Password reset should work in production!")
    else:
        print("\n🚨 Issues found - check Railway deployment configuration")
