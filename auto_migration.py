"""
Auto-migration for Railway - runs on app startup
Add this to your app.py to automatically run migration on deployment
"""

import os
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

def auto_migrate_password_reset():
    """Automatically add password reset fields on app startup"""
    
    # Only run in production
    if os.getenv('ENVIRONMENT') != 'production':
        return True
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.warning("DATABASE_URL not found - skipping migration")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
            """))
            
            existing = [row[0] for row in result.fetchall()]
            
            # Add missing columns
            if 'password_reset_token' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL'))
                logger.info("✅ Added password_reset_token column")
            
            if 'password_reset_expires' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL'))
                logger.info("✅ Added password_reset_expires column")
            
            conn.commit()
            logger.info("🎉 Password reset migration completed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

# Add this to your app.py
def init_database_migrations():
    """Initialize database migrations"""
    try:
        auto_migrate_password_reset()
    except Exception as e:
        logger.error(f"Database migration error: {e}")
        # Don't crash the app if migration fails
        pass
