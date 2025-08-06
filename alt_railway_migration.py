#!/usr/bin/env python3
"""
Alternative migration approach using psycopg2 directly with DATABASE_URL
"""

import os
import sys
import psycopg2

def run_migration():
    """Run the time fields migration using direct DATABASE_URL connection"""
    print("🚀 Starting time fields migration (alternative approach)...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print(f"🔗 Using DATABASE_URL: {database_url[:50]}...")
    
    try:
        # Connect directly using the DATABASE_URL
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("📦 Connected to database successfully")
        
        # Test connection first
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Check if table exists
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'event'
        """)
        
        tables = cur.fetchall()
        if not tables:
            print("❌ Event table not found")
            return False
        
        print("✅ Event table found")
        
        # Check existing columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"📋 Existing time columns: {existing_columns}")
        
        # Migration SQL - safer approach
        migrations = []
        
        if 'arrive_by_time' not in existing_columns:
            migrations.append("ALTER TABLE event ADD COLUMN arrive_by_time TIME;")
        
        if 'start_time' not in existing_columns:
            migrations.append("ALTER TABLE event ADD COLUMN start_time TIME;")
        
        if 'end_time' not in existing_columns:
            migrations.append("ALTER TABLE event ADD COLUMN end_time TIME;")
        
        if not migrations:
            print("✅ All time columns already exist - no migration needed")
            return True
        
        print(f"🔄 Executing {len(migrations)} migrations...")
        
        for i, migration in enumerate(migrations, 1):
            print(f"  {i}. {migration}")
            cur.execute(migration)
            conn.commit()
            print(f"  ✅ Migration {i} completed")
        
        # Verify final state
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            ORDER BY column_name
        """)
        
        final_columns = cur.fetchall()
        print(f"📊 Final state - {len(final_columns)} time columns:")
        
        for column in final_columns:
            print(f"  ✅ {column[0]} ({column[1]}, nullable: {column[2]})")
        
        cur.close()
        conn.close()
        
        if len(final_columns) == 3:
            print("🎉 All time fields successfully added!")
            return True
        else:
            print(f"⚠️  Only {len(final_columns)} out of 3 expected columns found")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == '__main__':
    success = run_migration()
    print("🎊 Migration completed successfully!" if success else "💥 Migration failed!")
    sys.exit(0 if success else 1)
