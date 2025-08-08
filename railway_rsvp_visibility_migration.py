#!/usr/bin/env python3
"""
Railway-specific migration for RSVP visibility setting
This migration adds the members_can_view_rsvp_status field to the organization table
for Railway PostgreSQL deployment
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection from Railway environment variables"""
    
    # Railway provides DATABASE_URL for PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Fallback to individual environment variables
        host = os.getenv('PGHOST')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE')
        user = os.getenv('PGUSER')
        password = os.getenv('PGPASSWORD')
        
        if all([host, database, user, password]):
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            logger.error("No database connection information found in environment variables")
            return None
    
    try:
        # Parse the DATABASE_URL
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        logger.info(f"✓ Connected to PostgreSQL database: {parsed.hostname}")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return None

def run_migration():
    """Add the members_can_view_rsvp_status column to the organization table"""
    
    logger.info("🚀 Starting RSVP visibility setting migration...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if the column already exists
        logger.info("Checking if members_can_view_rsvp_status column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='organization' 
            AND column_name='members_can_view_rsvp_status'
        """)
        
        if cursor.fetchone():
            logger.info("✓ Column 'members_can_view_rsvp_status' already exists in organization table")
            conn.close()
            return True
        
        logger.info("Adding 'members_can_view_rsvp_status' column to organization table...")
        
        # Add the new column with default value True (existing behavior)
        cursor.execute("""
            ALTER TABLE organization 
            ADD COLUMN members_can_view_rsvp_status BOOLEAN DEFAULT TRUE
        """)
        
        # Update existing organizations to have the default value
        cursor.execute("""
            UPDATE organization 
            SET members_can_view_rsvp_status = TRUE 
            WHERE members_can_view_rsvp_status IS NULL
        """)
        
        # Commit changes
        conn.commit()
        
        logger.info("✓ Successfully added 'members_can_view_rsvp_status' column to organization table")
        logger.info("✓ All existing organizations set to allow member RSVP visibility (default behavior)")
        
        # Verify the change
        cursor.execute("""
            SELECT COUNT(*) as org_count,
                   SUM(CASE WHEN members_can_view_rsvp_status = TRUE THEN 1 ELSE 0 END) as visible_count
            FROM organization
        """)
        
        result = cursor.fetchone()
        org_count, visible_count = result
        
        logger.info(f"Migration Verification:")
        logger.info(f"  Total organizations: {org_count}")
        logger.info(f"  Organizations with RSVP visibility enabled: {visible_count}")
        logger.info(f"  Organizations with RSVP visibility disabled: {org_count - visible_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("RSVP Visibility Setting Migration (Railway)")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now()}")
    
    # Check if we're in Railway environment
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    if railway_env:
        logger.info(f"Running in Railway environment: {railway_env}")
    else:
        logger.info("Running in local/non-Railway environment")
    
    # Run migration
    success = run_migration()
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("=" * 60)
        logger.error("❌ Migration failed!")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
