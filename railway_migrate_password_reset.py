"""
Simple Railway database migration for password reset
Add this to your Railway app as a one-time migration
"""

import os
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_password_reset_fields():
    """Add password reset fields to Railway database"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if fields already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
            """))
            
            existing = [row[0] for row in result.fetchall()]
            logger.info(f"Existing password reset columns: {existing}")
            
            # Add password_reset_token if not exists
            if 'password_reset_token' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL'))
                logger.info("✅ Added password_reset_token column")
            else:
                logger.info("✅ password_reset_token column already exists")
            
            # Add password_reset_expires if not exists
            if 'password_reset_expires' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL'))
                logger.info("✅ Added password_reset_expires column")
            else:
                logger.info("✅ password_reset_expires column already exists")
            
            conn.commit()
            logger.info("🎉 Password reset migration completed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_password_reset_fields()
    exit(0 if success else 1)
