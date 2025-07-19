#!/usr/bin/env python3
"""
Check user passwords and try to reset them if needed
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

def check_and_reset_passwords():
    """Check user passwords and reset if needed"""
    
    print("🔍 Checking user passwords...")
    
    # Use Railway database URL directly
    db_url = 'postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway'
    
    try:
        engine = create_engine(db_url)
        print("🔧 Connecting to Railway database...")
        
        with engine.connect() as conn:
            print("✅ Connected to database")
            
            # Check current users
            result = conn.execute(text('SELECT id, username, email, password_hash, super_admin FROM "user"'))
            users = result.fetchall()
            
            print(f"📊 Current users and their password hashes:")
            for user in users:
                print(f"  - {user[1]} ({user[2]}) - Super Admin: {user[4]}")
                print(f"    Password hash: {user[3][:50]}...")
            
            # Reset passwords for known users
            password_resets = [
                ("Harvey258", "password"),
                ("CBBB25", "password"),
                ("Rob123", "password"),
                ("WMBBA", "password")
            ]
            
            for username, new_password in password_resets:
                print(f"\n🔐 Resetting password for {username}...")
                
                # Generate new password hash
                new_hash = generate_password_hash(new_password)
                
                # Update password
                result = conn.execute(text(f"""
                    UPDATE "user" 
                    SET password_hash = '{new_hash}' 
                    WHERE username = '{username}'
                """))
                
                if result.rowcount > 0:
                    print(f"✅ Password reset for {username} to '{new_password}'")
                else:
                    print(f"⚠️  User {username} not found")
            
            conn.commit()
            print("\n✅ Password reset completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    check_and_reset_passwords()
