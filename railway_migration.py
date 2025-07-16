#!/usr/bin/env python3
"""
Railway Organization Migration Script
====================================

This script adds new organization profile fields to the database.
It's designed to run on Railway's environment.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from Railway environment variables"""
    # Railway typically uses DATABASE_URL
    for var_name in ['DATABASE_URL', 'POSTGRES_URL', 'POSTGRESQL_URL']:
        url = os.getenv(var_name)
        if url:
            logger.info(f"Found database URL in {var_name}")
            return url
    
    logger.error("❌ Could not find database URL in environment variables")
    return None

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except Exception as e:
        logger.error(f"Error checking column {column_name}: {e}")
        return False

def add_organization_columns(engine):
    """Add new organization profile columns"""
    logger.info("🔄 Adding organization profile columns...")
    
    # Define new columns to add
    new_columns = [
        ('rehearsal_address', 'TEXT'),
        ('contact_phone', 'VARCHAR(20)'),
        ('contact_email', 'VARCHAR(255)'),
        ('website', 'VARCHAR(255)'),
        ('facebook_url', 'VARCHAR(255)'),
        ('instagram_url', 'VARCHAR(255)'),
        ('twitter_url', 'VARCHAR(255)'),
        ('tiktok_url', 'VARCHAR(255)'),
        ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    ]
    
    added_columns = []
    
    with engine.connect() as conn:
        for column_name, column_type in new_columns:
            if not check_column_exists(engine, 'organization', column_name):
                try:
                    sql = f"ALTER TABLE organization ADD COLUMN {column_name} {column_type}"
                    logger.info(f"  Adding column: {column_name}")
                    conn.execute(text(sql))
                    conn.commit()
                    added_columns.append(column_name)
                    logger.info(f"  ✅ Added {column_name}")
                except SQLAlchemyError as e:
                    logger.error(f"  ❌ Failed to add {column_name}: {e}")
                    # Continue with other columns
            else:
                logger.info(f"  ✅ Column {column_name} already exists")
    
    return added_columns

def main():
    logger.info("🚀 Starting Railway Organization Migration")
    logger.info("=" * 50)
    
    # Get database URL
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ No database URL found in environment")
        sys.exit(1)
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Check if organization table exists
        inspector = inspect(engine)
        if 'organization' not in inspector.get_table_names():
            logger.error("❌ Organization table not found!")
            sys.exit(1)
        
        logger.info("✅ Organization table found")
        
        # Add new columns
        added_columns = add_organization_columns(engine)
        
        if added_columns:
            logger.info(f"🎉 Migration completed! Added {len(added_columns)} columns:")
            for col in added_columns:
                logger.info(f"  - {col}")
        else:
            logger.info("✅ All columns already exist - no migration needed")
        
        logger.info("=" * 50)
        logger.info("🎉 Migration successful!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
