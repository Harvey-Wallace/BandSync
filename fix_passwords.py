#!/usr/bin/env python3
"""
Fix all user passwords in the production database
"""

import psycopg2
from werkzeug.security import generate_password_hash

# Database connection
external_db_url = "postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@caboose.proxy.rlwy.net:46206/railway"

def fix_all_passwords():
    """Fix all user passwords in the database"""
    try:
        print("🔧 Fixing all user passwords...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Define default passwords for users
        user_passwords = {
            'testuser': 'testpass',
            'testuser2': 'testpass2',
            'testuser123': 'testpass123',
            'newuser123': 'newpass123',
            'testuser789': 'testpass789',
            'Rob123': 'Rob123pass'
        }
        
        # Get all users
        cur.execute("""
            SELECT id, username, email
            FROM "user" 
            ORDER BY id;
        """)
        
        users = cur.fetchall()
        for user_id, username, email in users:
            # Get password for this user
            password = user_passwords.get(username, 'defaultpass')
            
            # Generate new hash
            new_hash = generate_password_hash(password)
            
            # Update in database
            cur.execute("""
                UPDATE "user" 
                SET password_hash = %s 
                WHERE id = %s;
            """, (new_hash, user_id))
            
            print(f"✅ Updated password for {username} ({email}) -> '{password}'")
        
        conn.commit()
        conn.close()
        
        print("\n🎯 All user passwords have been fixed!")
        print("You can now log in with:")
        for username, password in user_passwords.items():
            print(f"  - {username} -> {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing passwords: {e}")
        return False

if __name__ == "__main__":
    print("🔧 BandSync Password Fix Tool")
    print("=" * 50)
    
    confirm = input("⚠️  This will reset all user passwords. Continue? (y/N): ")
    if confirm.lower().startswith('y'):
        fix_all_passwords()
    else:
        print("Cancelled.")
