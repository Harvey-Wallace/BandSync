#!/usr/bin/env python3

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Try different possible environment variable names
    for var_name in ['DATABASE_URL', 'POSTGRES_URL', 'POSTGRESQL_URL']:
        url = os.getenv(var_name)
        if url:
            logger.info(f"Found database URL in {var_name}")
            return url
    
    # If no URL found, try to construct from individual components
    host = os.getenv('PGHOST') or os.getenv('DB_HOST')
    port = os.getenv('PGPORT') or os.getenv('DB_PORT') or '5432'
    user = os.getenv('PGUSER') or os.getenv('DB_USER')
    password = os.getenv('PGPASSWORD') or os.getenv('DB_PASSWORD')
    database = os.getenv('PGDATABASE') or os.getenv('DB_NAME')
    
    if all([host, user, password, database]):
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        logger.info("Constructed database URL from components")
        return url
    
    logger.error("Could not find database connection information")
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

def migrate_organization_table(engine):
    """Add new columns to organization table"""
    logger.info("Starting organization table migration...")
    
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
    
    with engine.connect() as conn:
        # Check which columns already exist
        for column_name, column_type in new_columns:
            if not check_column_exists(engine, 'organization', column_name):
                try:
                    sql = f"ALTER TABLE organization ADD COLUMN {column_name} {column_type}"
                    logger.info(f"Adding column: {column_name}")
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Added column {column_name}")
                except SQLAlchemyError as e:
                    logger.error(f"❌ Failed to add column {column_name}: {e}")
                    # Continue with other columns
            else:
                logger.info(f"✅ Column {column_name} already exists")

def main():
    logger.info("🚀 Starting Railway deployment with migration")
    
    # Get database URL
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ No database URL found")
        sys.exit(1)
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Run migration
        migrate_organization_table(engine)
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
