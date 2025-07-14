"""
Add password reset fields to User model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from models import db, User
from sqlalchemy import text

def add_password_reset_fields():
    """Add password reset token and expiry fields to User table"""
    
    print("Adding password reset fields to User table...")
    
    try:
        # Add password_reset_token column
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN password_reset_token VARCHAR(255) NULL;
            """))
            
            # Add password_reset_expires column
            conn.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN password_reset_expires TIMESTAMP NULL;
            """))
            
            conn.commit()
        
        print("✅ Password reset fields added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding password reset fields: {e}")
        print("This might be because the fields already exist.")

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        add_password_reset_fields()
