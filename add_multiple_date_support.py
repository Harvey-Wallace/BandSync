#!/usr/bin/env python3
"""
Add Multiple Date Selection Support Migration
Adds EventPossibleDate and EventDateVote tables for multi-date event scheduling
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Set environment to avoid production-only migrations
os.environ['ENVIRONMENT'] = 'development'

from datetime import datetime
import psycopg2
from sqlalchemy import create_engine, text

def run_migration():
    """Add multiple date selection support to events"""
    
    print("🗄️  Adding multiple date selection support...")
    
    try:
        # Force local development for this migration
        database_url = 'sqlite:///backend/bandsync_local.db'
        print("🔗 Using local SQLite database for development...")
            
        engine = create_engine(database_url)
        is_sqlite = 'sqlite' in database_url
        
        with engine.connect() as conn:
            print("📋 Checking existing columns...")
            
            try:
                # Check existing columns (different syntax for SQLite vs PostgreSQL)
                if is_sqlite:
                    result = conn.execute(text("PRAGMA table_info(event)"))
                    existing_columns = [row[1] for row in result]  # Column name is at index 1
                else:
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='event' 
                        AND column_name IN ('has_multiple_dates', 'final_date_selected', 'date_selection_deadline')
                    """))
                    existing_columns = [row[0] for row in result]
                
                print(f"📋 Found existing columns: {existing_columns}")
                
                # Add missing columns
                if 'has_multiple_dates' not in existing_columns:
                    conn.execute(text("ALTER TABLE event ADD COLUMN has_multiple_dates BOOLEAN DEFAULT FALSE"))
                    print("✅ Added has_multiple_dates column")
                    
                if 'final_date_selected' not in existing_columns:
                    conn.execute(text("ALTER TABLE event ADD COLUMN final_date_selected BOOLEAN DEFAULT FALSE"))
                    print("✅ Added final_date_selected column")
                    
                if 'date_selection_deadline' not in existing_columns:
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE event ADD COLUMN date_selection_deadline DATETIME"))
                    else:
                        conn.execute(text("ALTER TABLE event ADD COLUMN date_selection_deadline TIMESTAMP"))
                    print("✅ Added date_selection_deadline column")
                
                # Create new tables
                print("📋 Creating EventPossibleDate table...")
                if is_sqlite:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS event_possible_dates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
                            date DATETIME NOT NULL,
                            end_date DATETIME,
                            arrive_by_time TIME,
                            start_time TIME,
                            end_time TIME,
                            vote_count INTEGER DEFAULT 0,
                            is_selected BOOLEAN DEFAULT FALSE,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS event_possible_dates (
                            id SERIAL PRIMARY KEY,
                            event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
                            date TIMESTAMP NOT NULL,
                            end_date TIMESTAMP,
                            arrive_by_time TIME,
                            start_time TIME,
                            end_time TIME,
                            vote_count INTEGER DEFAULT 0,
                            is_selected BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                print("✅ Created event_possible_dates table")
                
                print("📋 Creating EventDateVote table...")
                if is_sqlite:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS event_date_votes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                            possible_date_id INTEGER NOT NULL REFERENCES event_possible_dates(id) ON DELETE CASCADE,
                            event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
                            preference_order INTEGER DEFAULT 1,
                            can_attend BOOLEAN DEFAULT TRUE,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, possible_date_id)
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS event_date_votes (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                            possible_date_id INTEGER NOT NULL REFERENCES event_possible_dates(id) ON DELETE CASCADE,
                            event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
                            preference_order INTEGER DEFAULT 1,
                            can_attend BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, possible_date_id)
                        )
                    """))
                print("✅ Created event_date_votes table")
                
                # Update existing events
                print("📋 Updating existing events...")
                conn.execute(text("""
                    UPDATE event 
                    SET has_multiple_dates = 0, 
                        final_date_selected = 1 
                    WHERE has_multiple_dates IS NULL 
                    OR final_date_selected IS NULL
                """))
                
                conn.commit()
                print("✅ Migration completed successfully!")
                print("   - Added multiple date selection support")
                print("   - Created EventPossibleDate and EventDateVote tables")
                print("   - Updated existing events to use single-date mode")
                
            except Exception as e:
                print(f"❌ Migration failed: {e}")
                conn.rollback()
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    run_migration()
