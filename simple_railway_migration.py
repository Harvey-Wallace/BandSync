#!/usr/bin/env python3
"""
Simple time fields migration for Railway deployment
This file should be deployed and run as part of your Railway application startup
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def run_migration():
    """Run the time fields migration"""
    print("🚀 Starting time fields migration...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            port=parsed.port
        )
        
        cur = conn.cursor()
        
        print("📦 Connected to database successfully")
        
        # Migration SQL
        migration_sql = """
        DO $$
        BEGIN
            -- Add arrive_by_time column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'event' AND column_name = 'arrive_by_time') THEN
                ALTER TABLE event ADD COLUMN arrive_by_time TIME;
                RAISE NOTICE 'Added arrive_by_time column';
            ELSE
                RAISE NOTICE 'arrive_by_time column already exists';
            END IF;
            
            -- Add start_time column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'event' AND column_name = 'start_time') THEN
                ALTER TABLE event ADD COLUMN start_time TIME;
                RAISE NOTICE 'Added start_time column';
            ELSE
                RAISE NOTICE 'start_time column already exists';
            END IF;
            
            -- Add end_time column if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name = 'event' AND column_name = 'end_time') THEN
                ALTER TABLE event ADD COLUMN end_time TIME;
                RAISE NOTICE 'Added end_time column';
            ELSE
                RAISE NOTICE 'end_time column already exists';
            END IF;
        END
        $$;
        """
        
        print("🔄 Executing migration...")
        cur.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration SQL executed successfully")
        
        # Verify columns were added
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            ORDER BY column_name
        """)
        
        columns = cur.fetchall()
        print(f"📊 Found {len(columns)} time columns:")
        
        for column in columns:
            print(f"  ✅ {column[0]} ({column[1]}, nullable: {column[2]})")
        
        cur.close()
        conn.close()
        
        if len(columns) == 3:
            print("🎉 All time fields successfully added!")
            return True
        else:
            print(f"⚠️  Only {len(columns)} out of 3 expected columns found")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    print("🎊 Migration completed!" if success else "💥 Migration failed!")
    sys.exit(0 if success else 1)
