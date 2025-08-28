-- Multiple Dates Feature Migration SQL
-- Add support for events with multiple date options and voting
-- Run this in Railway PostgreSQL using: railway connect postgres

BEGIN;

-- Check if columns exist before adding them
DO $$ 
BEGIN
    -- Add has_multiple_dates column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'has_multiple_dates') THEN
        ALTER TABLE event ADD COLUMN has_multiple_dates BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added has_multiple_dates column';
    ELSE
        RAISE NOTICE 'has_multiple_dates column already exists';
    END IF;
    
    -- Add final_date_selected column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'final_date_selected') THEN
        ALTER TABLE event ADD COLUMN final_date_selected BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added final_date_selected column';
    ELSE
        RAISE NOTICE 'final_date_selected column already exists';
    END IF;
    
    -- Add date_selection_deadline column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'date_selection_deadline') THEN
        ALTER TABLE event ADD COLUMN date_selection_deadline TIMESTAMP;
        RAISE NOTICE 'Added date_selection_deadline column';
    ELSE
        RAISE NOTICE 'date_selection_deadline column already exists';
    END IF;
END $$;

-- Create event_possible_dates table
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
);

-- Create event_date_votes table
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
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_event_possible_dates_event_id ON event_possible_dates(event_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_event_id ON event_date_votes(event_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_user_id ON event_date_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_possible_date_id ON event_date_votes(possible_date_id);

-- Update existing events to have default values
UPDATE event 
SET has_multiple_dates = FALSE, 
    final_date_selected = TRUE 
WHERE has_multiple_dates IS NULL 
   OR final_date_selected IS NULL;

COMMIT;

-- Verify the migration
\echo 'Migration completed! Verifying results...'

SELECT 'has_multiple_dates' as column_name, 
       data_type, 
       is_nullable, 
       column_default
FROM information_schema.columns 
WHERE table_name = 'event' AND column_name = 'has_multiple_dates'
UNION ALL
SELECT 'final_date_selected' as column_name, 
       data_type, 
       is_nullable, 
       column_default
FROM information_schema.columns 
WHERE table_name = 'event' AND column_name = 'final_date_selected'
UNION ALL
SELECT 'date_selection_deadline' as column_name, 
       data_type, 
       is_nullable, 
       column_default
FROM information_schema.columns 
WHERE table_name = 'event' AND column_name = 'date_selection_deadline';

\echo 'Checking new tables...'
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('event_possible_dates', 'event_date_votes');

\echo 'Migration verification complete!'
