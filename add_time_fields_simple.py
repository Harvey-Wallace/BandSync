#!/usr/bin/env python3
"""
Simple migration script to add time fields to events table
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_url():
    """Get database URL from environment or config"""
    # Try to get from environment
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return db_url
    
    # Try to read from .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DATABASE_URL='):
                    return line.split('=', 1)[1].strip('"\'')
    
    # Try Railway environment
    railway_url = os.environ.get('RAILWAY_URL')
    if railway_url:
        return railway_url
        
    # Default fallback
    return "postgresql://postgres:password@localhost:5432/bandsync"

def run_migration():
    """Run the time fields migration"""
    db_url = get_database_url()
    print(f"Using database URL: {db_url}")
    
    # Parse the database URL
    parsed = urlparse(db_url)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading /
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        print("Running time fields migration...")
        
        # Add arrive_by_time column if it doesn't exist
        try:
            cursor.execute("""
                ALTER TABLE event ADD COLUMN arrive_by_time TIME;
            """)
            print("✅ Added arrive_by_time column")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print("ℹ️  arrive_by_time column already exists")
            else:
                print(f"❌ Error adding arrive_by_time column: {e}")
        
        # Add start_time column if it doesn't exist
        try:
            cursor.execute("""
                ALTER TABLE event ADD COLUMN start_time TIME;
            """)
            print("✅ Added start_time column")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print("ℹ️  start_time column already exists")
            else:
                print(f"❌ Error adding start_time column: {e}")
        
        # Add end_time column if it doesn't exist
        try:
            cursor.execute("""
                ALTER TABLE event ADD COLUMN end_time TIME;
            """)
            print("✅ Added end_time column")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print("ℹ️  end_time column already exists")
            else:
                print(f"❌ Error adding end_time column: {e}")
        
        # Commit the changes
        conn.commit()
        
        # Verify the columns were added
        print("\nVerifying new columns...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        for column in columns:
            print(f"✅ Column '{column[0]}' exists with type '{column[1]}'")
        
        if len(columns) == 3:
            print("✅ All time fields successfully added to events table!")
        else:
            print(f"⚠️  Only {len(columns)} out of 3 expected columns were found")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    run_migration()
