-- Safe Database Reset Script - handles missing tables gracefully
-- Run these commands one by one in psql

-- 1. Show all existing tables
\echo 'Existing tables:'
\dt

-- 2. Check what tables actually exist and get their row counts
\echo 'Current data in existing tables:'

-- Check each table individually with error handling
DO $$
DECLARE
    table_record RECORD;
    table_count INTEGER;
BEGIN
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_record.tablename) INTO table_count;
        RAISE NOTICE '% : % rows', table_record.tablename, table_count;
    END LOOP;
END $$;

-- 3. Disable foreign key constraints
SET session_replication_role = replica;

-- 4. Clear all tables that exist (use DO block for safe deletion)
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename DESC  -- Delete in reverse order to handle dependencies
    LOOP
        EXECUTE format('DELETE FROM %I', table_record.tablename);
        RAISE NOTICE 'Cleared table: %', table_record.tablename;
    END LOOP;
END $$;

-- 5. Reset all sequences
DO $$
DECLARE
    seq_record RECORD;
BEGIN
    FOR seq_record IN 
        SELECT sequencename 
        FROM pg_sequences 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('SELECT setval(%L, 1, false)', seq_record.sequencename);
        RAISE NOTICE 'Reset sequence: %', seq_record.sequencename;
    END LOOP;
END $$;

-- 6. Re-enable foreign key constraints
SET session_replication_role = DEFAULT;

-- 7. Final verification
\echo 'Final verification - all counts should be 0:'
DO $$
DECLARE
    table_record RECORD;
    table_count INTEGER;
BEGIN
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_record.tablename) INTO table_count;
        RAISE NOTICE '% : % rows', table_record.tablename, table_count;
    END LOOP;
END $$;

\echo 'Database reset complete!'
