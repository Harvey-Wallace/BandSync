#!/usr/bin/env python3
"""
Railway-specific migration runner
Connects directly to Railway database and runs magic link migration
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def run_railway_migration():
    """Run magic link migration on Railway database"""
    
    # Get Railway database URL from environment
    railway_db_url = os.getenv('DATABASE_URL')
    
    if not railway_db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print("🚀 Connecting to Railway database...")
    print(f"🔗 Database URL: {railway_db_url[:50]}...")
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(railway_db_url)
        cur = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check existing columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires');
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"📊 Existing magic link columns: {existing_columns}")
        
        # Add magic_link_token if it doesn't exist
        if 'magic_link_token' not in existing_columns:
            print("➕ Adding magic_link_token column...")
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_token VARCHAR(255);
            """)
            print("✅ magic_link_token column added")
        else:
            print("ℹ️  magic_link_token column already exists")
        
        # Add magic_link_expires if it doesn't exist
        if 'magic_link_expires' not in existing_columns:
            print("➕ Adding magic_link_expires column...")
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_expires TIMESTAMP;
            """)
            print("✅ magic_link_expires column added")
        else:
            print("ℹ️  magic_link_expires column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires')
            ORDER BY column_name;
        """)
        
        print("\n📋 Final column verification:")
        for row in cur.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
        
        cur.close()
        conn.close()
        
        print("\n🎯 Railway magic link migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Railway migration error: {e}")
        return False

if __name__ == "__main__":
    print("🎵 BandSync Railway Magic Link Migration")
    print("=" * 50)
    
    success = run_railway_migration()
    
    if success:
        print("\n✅ Migration completed - magic link authentication is ready!")
    else:
        print("\n❌ Migration failed - check Railway database connection")
