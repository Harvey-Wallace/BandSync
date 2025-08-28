#!/usr/bin/env python3
"""
Railway Multiple Date Support Migration
Add multiple date selection support to the production PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text

def run_migration():
    """Add multiple date selection support to events on Railway"""
    
    print("🗄️  Adding multiple date selection support to Railway database...")
    
    # Get the Railway DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"🔗 Connecting to PostgreSQL database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("📋 Checking existing columns...")
            
            # Check existing columns in PostgreSQL
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
            else:
                print("ℹ️  has_multiple_dates column already exists")
                
            if 'final_date_selected' not in existing_columns:
                conn.execute(text("ALTER TABLE event ADD COLUMN final_date_selected BOOLEAN DEFAULT FALSE"))
                print("✅ Added final_date_selected column")
            else:
                print("ℹ️  final_date_selected column already exists")
                
            if 'date_selection_deadline' not in existing_columns:
                conn.execute(text("ALTER TABLE event ADD COLUMN date_selection_deadline TIMESTAMP"))
                print("✅ Added date_selection_deadline column")
            else:
                print("ℹ️  date_selection_deadline column already exists")
            
            # Create EventPossibleDate table
            print("📋 Creating event_possible_dates table...")
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
            
            # Create EventDateVote table
            print("📋 Creating event_date_votes table...")
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
            
            # Create indexes for performance
            print("📋 Creating indexes...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_event_possible_dates_event_id ON event_possible_dates(event_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_event_date_votes_event_id ON event_date_votes(event_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_event_date_votes_user_id ON event_date_votes(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_event_date_votes_possible_date_id ON event_date_votes(possible_date_id)"))
            print("✅ Created performance indexes")
            
            # Update existing events
            print("📋 Updating existing events...")
            conn.execute(text("""
                UPDATE event 
                SET has_multiple_dates = FALSE, 
                    final_date_selected = TRUE 
                WHERE has_multiple_dates IS NULL 
                OR final_date_selected IS NULL
            """))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added multiple date selection support")
            print("   - Created EventPossibleDate and EventDateVote tables")
            print("   - Updated existing events to use single-date mode")
            print("   - Created performance indexes")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
