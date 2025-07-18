#!/usr/bin/env python3
"""
Check user table structure and fix Super Admin
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_and_fix_users():
    """Check user table and fix Super Admin"""
    
    print("🔍 Checking user table structure and fixing Super Admin...")
    
    # Use Railway database URL directly
    db_url = 'postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway'
    
    try:
        engine = create_engine(db_url)
        print("🔧 Connecting to Railway database...")
        
        with engine.connect() as conn:
            print("✅ Connected to database")
            
            # Check user table structure
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user'
            """))
            
            columns = result.fetchall()
            print(f"📋 Columns in user table:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check if super_admin column exists
            column_names = [col[0] for col in columns]
            
            if 'super_admin' not in column_names:
                print("➕ Adding super_admin column...")
                conn.execute(text('ALTER TABLE "user" ADD COLUMN super_admin BOOLEAN DEFAULT FALSE'))
                conn.commit()
                print("✅ super_admin column added")
            else:
                print("✅ super_admin column already exists")
            
            # Check current users
            result = conn.execute(text('SELECT id, username, email, super_admin FROM "user"'))
            users = result.fetchall()
            
            print(f"📊 Current users:")
            for user in users:
                super_admin_val = user[3] if len(user) > 3 else False
                print(f"  - {user[1]} ({user[2]}) - Super Admin: {super_admin_val}")
            
            # Set Harvey258 as Super Admin
            result = conn.execute(text('UPDATE "user" SET super_admin = TRUE WHERE username = \'Harvey258\''))
            print(f"🔧 Updated {result.rowcount} users to Super Admin")
            
            if result.rowcount == 0:
                print("⚠️  Harvey258 user not found. Available users:")
                result = conn.execute(text('SELECT username FROM "user"'))
                usernames = [row[0] for row in result.fetchall()]
                for username in usernames:
                    print(f"  - {username}")
            
            conn.commit()
            print("✅ User table fix completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    check_and_fix_users()
