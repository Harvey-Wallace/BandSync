"""
Railway-compatible database migration for password reset fields
Run this after deployment to add password reset fields to production database
"""

import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

def add_password_reset_fields_production():
    """Add password reset fields to production database"""
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 Connecting to database: {urlparse(database_url).hostname}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires');
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'password_reset_token' in existing_columns:
                print("✅ password_reset_token column already exists")
            else:
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN password_reset_token VARCHAR(255) NULL;
                """))
                print("✅ Added password_reset_token column")
            
            if 'password_reset_expires' in existing_columns:
                print("✅ password_reset_expires column already exists")
            else:
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN password_reset_expires TIMESTAMP NULL;
                """))
                print("✅ Added password_reset_expires column")
            
            conn.commit()
            print("🎉 Password reset fields migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        return False

if __name__ == "__main__":
    success = add_password_reset_fields_production()
    if success:
        print("\n🚀 Ready for password reset functionality!")
    else:
        print("\n❌ Migration failed - check database connection and permissions")
