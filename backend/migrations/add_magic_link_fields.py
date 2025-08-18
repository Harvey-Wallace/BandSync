"""
Add magic link authentication fields to User model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from models import db, User
from sqlalchemy import text

def add_magic_link_fields():
    """Add magic link token and expiry fields to User table"""
    
    print("🔧 Adding magic link fields to User table...")
    
    try:
        # Check if fields already exist
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires');
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"📊 Existing magic link columns: {existing_columns}")
        
        # Add magic_link_token if it doesn't exist
        if 'magic_link_token' not in existing_columns:
            print("➕ Adding magic_link_token column...")
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_token VARCHAR(255);
            """))
            print("✅ magic_link_token column added")
        else:
            print("ℹ️  magic_link_token column already exists")
        
        # Add magic_link_expires if it doesn't exist
        if 'magic_link_expires' not in existing_columns:
            print("➕ Adding magic_link_expires column...")
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_expires TIMESTAMP;
            """))
            print("✅ magic_link_expires column added")
        else:
            print("ℹ️  magic_link_expires column already exists")
        
        # Commit the changes
        db.session.commit()
        print("🎯 Magic link fields migration completed successfully!")
        
        # Verify the columns were added
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires')
            ORDER BY column_name;
        """))
        
        print("\n📋 Final column verification:")
        for row in result.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding magic link fields: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        add_magic_link_fields()
