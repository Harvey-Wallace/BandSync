#!/usr/bin/env python3
"""
Simple script to add missing columns to organization table
This is designed to be run in a Railway environment
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_add_columns():
    """Check if columns exist and add them if they don't"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if organization table exists
            inspector = inspect(engine)
            if 'organization' not in inspector.get_table_names():
                logger.error("Organization table does not exist")
                return False
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('organization')]
            logger.info(f"Existing columns: {existing_columns}")
            
            # Define columns to add
            new_columns = [
                ('rehearsal_address', 'TEXT'),
                ('contact_phone', 'VARCHAR(20)'),
                ('contact_email', 'VARCHAR(120)'),
                ('website', 'VARCHAR(255)'),
                ('facebook_url', 'VARCHAR(255)'),
                ('instagram_url', 'VARCHAR(255)'),
                ('twitter_url', 'VARCHAR(255)'),
                ('tiktok_url', 'VARCHAR(255)'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            # Add missing columns
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    try:
                        logger.info(f"Adding column: {column_name}")
                        conn.execute(text(f"ALTER TABLE organization ADD COLUMN {column_name} {column_type}"))
                        conn.commit()
                        logger.info(f"Successfully added column: {column_name}")
                    except (OperationalError, ProgrammingError) as e:
                        logger.error(f"Failed to add column {column_name}: {e}")
                        if "already exists" not in str(e).lower():
                            return False
                else:
                    logger.info(f"Column {column_name} already exists")
            
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    success = check_and_add_columns()
    sys.exit(0 if success else 1)
