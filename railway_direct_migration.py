#!/usr/bin/env python3
"""
Direct Railway Database Migration Runner
Connects to Railway PostgreSQL and runs magic link migration
"""

import psycopg2
import sys
import os
from urllib.parse import urlparse

def get_railway_db_url():
    """Get Railway database URL from user input"""
    print("🚂 Railway Database Connection Setup")
    print("=" * 50)
    
    print("\n📋 You need your Railway PostgreSQL connection string.")
    print("   To get it:")
    print("   1. Go to Railway dashboard")
    print("   2. Click your PostgreSQL service")
    print("   3. Go to 'Connect' or 'Variables' tab")
    print("   4. Copy the 'DATABASE_URL' or 'PostgreSQL Connection URL'")
    print("   5. It looks like: postgresql://postgres:password@host:port/railway")
    
    db_url = input("\n🔗 Paste your Railway DATABASE_URL here: ").strip()
    
    if not db_url:
        print("❌ No database URL provided")
        return None
    
    # Validate URL format
    try:
        parsed = urlparse(db_url)
        if parsed.scheme not in ['postgresql', 'postgres']:
            print("❌ Invalid PostgreSQL URL - should start with postgresql://")
            return None
        
        print(f"✅ Valid PostgreSQL URL detected")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        
        return db_url
        
    except Exception as e:
        print(f"❌ Error parsing database URL: {e}")
        return None

def run_magic_link_migration(db_url):
    """Run the magic link migration on Railway database"""
    
    print("\n🔧 Running Magic Link Migration...")
    print("=" * 40)
    
    try:
        # Connect to Railway database
        print("📡 Connecting to Railway database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check existing columns
        print("\n📊 Checking existing columns...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires');
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"   Existing magic link columns: {existing_columns}")
        
        migration_needed = False
        
        # Add magic_link_token if it doesn't exist
        if 'magic_link_token' not in existing_columns:
            print("\n➕ Adding magic_link_token column...")
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_token VARCHAR(255);
            """)
            print("✅ magic_link_token column added")
            migration_needed = True
        else:
            print("ℹ️  magic_link_token column already exists")
        
        # Add magic_link_expires if it doesn't exist
        if 'magic_link_expires' not in existing_columns:
            print("\n➕ Adding magic_link_expires column...")
            cur.execute("""
                ALTER TABLE "user" 
                ADD COLUMN magic_link_expires TIMESTAMP;
            """)
            print("✅ magic_link_expires column added")
            migration_needed = True
        else:
            print("ℹ️  magic_link_expires column already exists")
        
        if migration_needed:
            # Commit changes
            conn.commit()
            print("\n💾 Migration committed to database")
        else:
            print("\n✨ No migration needed - columns already exist")
        
        # Verify final state
        print("\n🔍 Verifying migration...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='user' 
            AND column_name IN ('magic_link_token', 'magic_link_expires')
            ORDER BY column_name;
        """)
        
        print("\n📋 Final column verification:")
        for row in cur.fetchall():
            print(f"   ✅ {row[0]}: {row[1]} (nullable: {row[2]})")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Railway magic link migration completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Test email login at your Railway URL")
        print("   2. Test magic link functionality")
        print("   3. Both features should now work!")
        
        return True
        
    except psycopg2.OperationalError as e:
        if "could not translate host name" in str(e):
            print("❌ Database connection failed - check your Railway database URL")
            print("   Make sure you copied the external connection URL, not internal")
        else:
            print(f"❌ Database connection error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def test_authentication_endpoints(db_url):
    """Test if the authentication endpoints work after migration"""
    
    print("\n🧪 Testing Authentication Features...")
    print("=" * 40)
    
    # Extract host from database URL to build API URL
    try:
        parsed = urlparse(db_url)
        # Try to guess the app URL from database host
        if 'railway.app' in parsed.hostname:
            # This is a Railway external connection
            app_url = input("\n🌐 Enter your Railway app URL (e.g., https://app.bandsync.co.uk): ").strip()
        else:
            app_url = input("\n🌐 Enter your app URL to test: ").strip()
        
        if app_url:
            import requests
            
            print(f"\n🔗 Testing {app_url}...")
            
            # Test magic link endpoint
            try:
                response = requests.post(f"{app_url}/api/auth/magic-link-request", 
                                       json={"email": "test@example.com"}, 
                                       timeout=10)
                
                if response.status_code == 200:
                    print("✅ Magic link endpoint is working!")
                elif response.status_code == 404:
                    print("⚠️  Magic link endpoint not deployed yet")
                elif response.status_code == 405:
                    print("⚠️  Magic link endpoint exists but may need frontend update")
                else:
                    print(f"⚠️  Magic link endpoint returned: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Could not test magic link endpoint: {e}")
            
    except Exception as e:
        print(f"⚠️  Could not test endpoints: {e}")

def main():
    print("🎵 BandSync Railway Database Migration Tool")
    print("=" * 60)
    
    # Get Railway database URL
    db_url = get_railway_db_url()
    if not db_url:
        print("\n❌ Cannot proceed without database URL")
        sys.exit(1)
    
    # Run migration
    success = run_magic_link_migration(db_url)
    
    if success:
        # Test endpoints
        test_authentication_endpoints(db_url)
        
        print("\n🎯 Migration Summary:")
        print("=" * 30)
        print("✅ Database migration: COMPLETED")
        print("🔧 Features ready: Email login + Magic links")
        print("🌐 Test at your Railway URL")
    else:
        print("\n❌ Migration failed - check database connection")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
