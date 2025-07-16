-- Migration to add time fields to events table
-- This adds arrive_by_time, start_time, and end_time fields

DO $$
BEGIN
    -- Add arrive_by_time column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'arrive_by_time') THEN
        ALTER TABLE event ADD COLUMN arrive_by_time TIME;
    END IF;
    
    -- Add start_time column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'start_time') THEN
        ALTER TABLE event ADD COLUMN start_time TIME;
    END IF;
    
    -- Add end_time column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'event' AND column_name = 'end_time') THEN
        ALTER TABLE event ADD COLUMN end_time TIME;
    END IF;
END $$;
