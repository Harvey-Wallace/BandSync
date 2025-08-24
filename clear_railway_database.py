#!/usr/bin/env python3
"""
Clear Railway Database Script
=============================
This script will completely clear all users and organizations from the Railway database,
giving you a fresh start for the app.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_railway_database_url():
    """Try to get the Railway database URL from environment or use recent known URLs"""
    
    # Try environment variable first
    env_db_url = os.getenv('DATABASE_URL')
    if env_db_url and 'railway' in env_db_url:
        return env_db_url
    
    # Recent known external URLs (try in order of most recent)
    known_urls = [
        "postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@shuttle.proxy.rlwy.net:40111/railway",
        "postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@caboose.proxy.rlwy.net:46206/railway",
        "postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway",
        "postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@postgres.railway.internal:5432/railway"
    ]
    
    print("🔍 Testing database connections...")
    
    for url in known_urls:
        try:
            conn = psycopg2.connect(url)
            conn.close()
            print(f"✅ Connected successfully to: {url[:50]}...")
            return url
        except Exception as e:
            print(f"❌ Failed to connect to: {url[:50]}... - {str(e)[:50]}")
    
    return None

def clear_database():
    """Clear all data from the Railway database"""
    
    print("🗑️  BandSync Railway Database Cleaner")
    print("=" * 50)
    print("⚠️  WARNING: This will delete ALL data!")
    print("   - All users")
    print("   - All organizations") 
    print("   - All events")
    print("   - All RSVPs")
    print("   - All custom fields")
    print("   - Everything else!")
    print()
    
    # Get database URL
    database_url = get_railway_database_url()
    if not database_url:
        print("❌ Could not connect to any Railway database!")
        print("💡 Please check your Railway database status or update the URLs in this script.")
        return False
    
    # Ask for confirmation
    confirm = input("Are you sure you want to delete ALL data? (type 'DELETE_EVERYTHING' to confirm): ")
    if confirm != 'DELETE_EVERYTHING':
        print("❌ Operation cancelled - you must type 'DELETE_EVERYTHING' exactly")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print(f"\n✅ Connected to Railway database")
        
        # First, let's see what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 Found {len(existing_tables)} tables:")
        for table in existing_tables:
            print(f"   - {table}")
        
        # Disable foreign key checks temporarily
        cursor.execute("SET session_replication_role = replica;")
        
        # Clear all tables in the correct order (to avoid foreign key issues)
        # Order matters due to foreign key constraints
        tables_to_clear = [
            'rsvp',                    # References events and users
            'event_rsvps',             # References events and users  
            'user_organizations',      # References users and organizations
            'custom_field_responses',  # References custom_fields
            'custom_fields',           # References events
            'event_templates',         # References organizations
            'events',                  # References organizations
            'email_preferences',       # References users
            'organization_profile',    # References organizations
            'section',                 # References organizations
            'event_category',          # References organizations
            'user',                    # Main user table
            'organization'             # Main organization table
        ]
        
        print(f"\n🧹 Clearing tables...")
        total_rows_deleted = 0
        
        for table in tables_to_clear:
            if table in existing_tables:
                try:
                    cursor.execute(f'DELETE FROM "{table}";')
                    rows_deleted = cursor.rowcount
                    total_rows_deleted += rows_deleted
                    print(f"   ✅ Cleared {table}: {rows_deleted} rows deleted")
                except Exception as e:
                    print(f"   ⚠️  Warning clearing {table}: {e}")
            else:
                print(f"   ⏭️  Skipped {table}: table doesn't exist")
        
        # Reset sequences (auto-increment counters)
        print(f"\n🔄 Resetting sequences...")
        
        # Get all sequences in the database
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public';
        """)
        sequences = [row[0] for row in cursor.fetchall()]
        
        for seq in sequences:
            try:
                cursor.execute(f'ALTER SEQUENCE "{seq}" RESTART WITH 1;')
                print(f"   ✅ Reset sequence {seq}")
            except Exception as e:
                print(f"   ⚠️  Warning resetting {seq}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Database cleared successfully!")
        print(f"🎉 Deleted {total_rows_deleted} total rows")
        
        # Verify the cleanup
        print(f"\n🔍 Verifying cleanup...")
        verification_tables = ['user', 'organization', 'events', 'rsvp']
        all_clean = True
        
        for table in verification_tables:
            if table in existing_tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                count = cursor.fetchone()[0]
                status = "✅" if count == 0 else "❌"
                print(f"   {status} {table}: {count} rows remaining")
                if count > 0:
                    all_clean = False
        
        cursor.close()
        conn.close()
        
        if all_clean:
            print(f"\n🎉 SUCCESS: Database is completely clean!")
        else:
            print(f"\n⚠️  Some tables still have data - check the warnings above")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def main():
    """Main function"""
    success = clear_database()
    
    if success:
        print(f"\n🚀 Database is now clean and ready for fresh setup!")
        print(f"You can now:")
        print(f"1. 🌐 Visit your BandSync app in a browser")
        print(f"2. 📝 Register new users through the web interface")
        print(f"3. 🏢 Create new organizations")
        print(f"4. 👑 Set up super admin users")
        print(f"5. 🎵 Start managing your band fresh!")
    else:
        print(f"\n❌ Database clearing failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
