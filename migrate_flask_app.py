#!/usr/bin/env python3
"""
Simple Railway migration using Flask app context
This script uses the existing Flask app and database connection
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def run_migration():
    """Run the migration using Flask app context"""
    try:
        # Import Flask app components
        from app import app
        from models import db
        from sqlalchemy import text
        
        with app.app_context():
            # Check if columns exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            print(f"🔍 Found existing columns: {existing_columns}")
            
            # Add missing columns
            if 'password_reset_token' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN password_reset_token VARCHAR(255) NULL
                """))
                print("✅ Added password_reset_token column")
            else:
                print("ℹ️  password_reset_token column already exists")
            
            if 'password_reset_expires' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN password_reset_expires TIMESTAMP NULL
                """))
                print("✅ Added password_reset_expires column")
            else:
                print("ℹ️  password_reset_expires column already exists")
            
            # Commit the changes
            db.session.commit()
            print("🎉 Password reset migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Railway password reset migration...")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Ready to deploy password reset functionality!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
