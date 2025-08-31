#!/usr/bin/env python3
"""
Simple subscription tables migration
Creates subscription and payment history tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("🔄 Starting subscription tables migration...")
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Try local SQLite database
            database_url = 'sqlite:///bandsync_local.db'
            logger.info("Using local SQLite database")
        else:
            logger.info("Using Railway PostgreSQL database")
        
        # Create engine
        engine = create_engine(database_url)
        
        # SQL for creating subscription table
        subscription_table_sql = """
        CREATE TABLE IF NOT EXISTS subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL UNIQUE,
            tier VARCHAR(20) NOT NULL DEFAULT 'free',
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            current_user_count INTEGER NOT NULL DEFAULT 0,
            max_users INTEGER DEFAULT 5,
            stripe_customer_id VARCHAR(255),
            stripe_subscription_id VARCHAR(255),
            billing_period_start TIMESTAMP,
            billing_period_end TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organization (id)
        );
        """
        
        # SQL for creating payment history table
        payment_history_table_sql = """
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            stripe_payment_intent_id VARCHAR(255) NOT NULL,
            amount INTEGER NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'usd',
            status VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organization (id)
        );
        """
        
        with engine.connect() as conn:
            # Create subscription table
            logger.info("📋 Creating subscription table...")
            conn.execute(text(subscription_table_sql))
            logger.info("✅ Subscription table created")
            
            # Create payment history table
            logger.info("📋 Creating payment_history table...")
            conn.execute(text(payment_history_table_sql))
            logger.info("✅ Payment history table created")
            
            # Commit the transaction
            conn.commit()
            
            logger.info("🎉 Migration completed successfully!")
            
    except OperationalError as e:
        if "already exists" in str(e):
            logger.info("ℹ️ Tables already exist, skipping creation")
        else:
            logger.error(f"❌ Database error: {str(e)}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
