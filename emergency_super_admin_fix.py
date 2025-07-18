#!/usr/bin/env python3
"""
Emergency fix for Super Admin login issues
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def emergency_fix():
    """Emergency fix for Super Admin login issues"""
    
    print("🚨 Emergency fix for Super Admin login issues...")
    
    # Use Railway database URL directly
    db_url = 'postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway'
    
    try:
        engine = create_engine(db_url)
        print("🔧 Connecting to Railway database...")
        
        with engine.connect() as conn:
            print("✅ Connected to database")
            
            # First, check if super_admin column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'super_admin'
            """))
            
            columns = [row[0] for row in result.fetchall()]
            
            if 'super_admin' not in columns:
                print("➕ Adding super_admin column...")
                conn.execute(text('ALTER TABLE users ADD COLUMN super_admin BOOLEAN DEFAULT FALSE'))
                conn.commit()
                print("✅ super_admin column added")
            else:
                print("✅ super_admin column already exists")
            
            # Check current users
            result = conn.execute(text("SELECT id, username, email, super_admin FROM users"))
            users = result.fetchall()
            
            print(f"📊 Current users:")
            for user in users:
                print(f"  - {user[1]} ({user[2]}) - Super Admin: {user[3]}")
            
            # Set Harvey258 as Super Admin
            result = conn.execute(text("UPDATE users SET super_admin = TRUE WHERE username = 'Harvey258'"))
            print(f"🔧 Updated {result.rowcount} users to Super Admin")
            
            conn.commit()
            print("✅ Emergency fix completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    emergency_fix()
