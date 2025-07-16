#!/usr/bin/env python3
"""
Minimal migration script to add time fields to events table
This script connects directly to the database without requiring the full Flask app
"""

import os
import sys
import logging
import psycopg2
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Check for Railway environment variables
    railway_vars = [
        'RAILWAY_DATABASE_URL',
        'DATABASE_URL',
        'POSTGRES_URL',
        'PGURL'
    ]
    
    for var in railway_vars:
        url = os.environ.get(var)
        if url:
            logger.info(f"Found database URL from {var}")
            return url
    
    # Check for individual Railway PostgreSQL variables
    host = os.environ.get('PGHOST')
    port = os.environ.get('PGPORT', '5432')
    database = os.environ.get('PGDATABASE')
    username = os.environ.get('PGUSER')
    password = os.environ.get('PGPASSWORD')
    
    if all([host, database, username, password]):
        url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        logger.info("Constructed database URL from individual variables")
        return url
    
    # Fallback to local database
    logger.warning("No Railway database URL found, using local fallback")
    return "postgresql://postgres:password@localhost:5432/bandsync"

def run_minimal_migration():
    """Run the time fields migration with minimal dependencies"""
    logger.info("🚀 Starting minimal time fields migration...")
    
    try:
        db_url = get_database_url()
        logger.info(f"Database URL: {db_url[:50]}...")
        
        # Parse the database URL
        parsed = urlparse(db_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading /
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        logger.info("📦 Database connection established")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing time columns: {existing_columns}")
        
        # Add arrive_by_time column if it doesn't exist
        if 'arrive_by_time' not in existing_columns:
            logger.info("Adding arrive_by_time column...")
            cursor.execute("ALTER TABLE event ADD COLUMN arrive_by_time TIME;")
            logger.info("✅ Added arrive_by_time column")
        else:
            logger.info("ℹ️  arrive_by_time column already exists")
        
        # Add start_time column if it doesn't exist
        if 'start_time' not in existing_columns:
            logger.info("Adding start_time column...")
            cursor.execute("ALTER TABLE event ADD COLUMN start_time TIME;")
            logger.info("✅ Added start_time column")
        else:
            logger.info("ℹ️  start_time column already exists")
        
        # Add end_time column if it doesn't exist
        if 'end_time' not in existing_columns:
            logger.info("Adding end_time column...")
            cursor.execute("ALTER TABLE event ADD COLUMN end_time TIME;")
            logger.info("✅ Added end_time column")
        else:
            logger.info("ℹ️  end_time column already exists")
        
        # Commit the changes
        conn.commit()
        logger.info("💾 Changes committed to database")
        
        # Verify the columns were added
        logger.info("🔍 Verifying new columns...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        logger.info(f"📊 Found {len(columns)} time columns:")
        
        for column in columns:
            logger.info(f"  ✅ {column[0]} ({column[1]}, nullable: {column[2]})")
        
        if len(columns) == 3:
            logger.info("🎉 All time fields successfully added to events table!")
            
            # Test the columns by running a simple query
            logger.info("🧪 Testing columns with a simple query...")
            cursor.execute("""
                SELECT COUNT(*) as event_count,
                       COUNT(arrive_by_time) as arrive_count,
                       COUNT(start_time) as start_count,
                       COUNT(end_time) as end_count
                FROM event
            """)
            
            result = cursor.fetchone()
            logger.info(f"📈 Found {result[0]} total events")
            logger.info(f"📊 Events with arrive_by_time: {result[1]}")
            logger.info(f"📊 Events with start_time: {result[2]}")
            logger.info(f"📊 Events with end_time: {result[3]}")
            
            cursor.close()
            conn.close()
            
            return True
        else:
            logger.warning(f"⚠️  Only {len(columns)} out of 3 expected columns were found")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    success = run_minimal_migration()
    if success:
        logger.info("🎊 Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)
