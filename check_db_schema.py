#!/usr/bin/env python3
"""
Check database schema for time fields from within Railway deployment
"""

import os
import sys

def check_database_schema():
    print("🔍 Checking database schema for time fields...")
    
    try:
        import psycopg2
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
        
        print(f"🔗 Connecting to database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("✅ Connected successfully")
        
        # Check current columns in event table
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'event'
            ORDER BY column_name
        """)
        
        all_columns = cur.fetchall()
        print(f"📊 Event table has {len(all_columns)} columns")
        
        # Check specifically for time fields
        time_columns = [col for col in all_columns if col[0] in ['arrive_by_time', 'start_time', 'end_time']]
        
        print(f"⏰ Found {len(time_columns)} time columns:")
        for col in time_columns:
            print(f"  ✅ {col[0]} ({col[1]}, nullable: {col[2]})")
        
        if len(time_columns) == 0:
            print("❌ No time columns found - migration needs to run")
            print("📋 All event table columns:")
            for col in all_columns:
                print(f"  - {col[0]} ({col[1]})")
        else:
            print("🎉 Time columns exist in database!")
        
        cur.close()
        conn.close()
        
        return len(time_columns) == 3
        
    except ImportError as e:
        print(f"❌ Missing psycopg2: {e}")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    success = check_database_schema()
    sys.exit(0 if success else 1)
