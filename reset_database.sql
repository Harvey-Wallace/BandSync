-- Complete Database Reset Script for Railway PostgreSQL
-- Run these commands step by step in your psql session

-- 1. First, let's see what's in the database
\echo 'Current table counts:'
SELECT 'users' as table_name, COUNT(*) as count FROM "user"
UNION ALL
SELECT 'organizations', COUNT(*) FROM "organization" 
UNION ALL
SELECT 'events', COUNT(*) FROM "events"
UNION ALL
SELECT 'user_organizations', COUNT(*) FROM "user_organizations"
UNION ALL
SELECT 'event_rsvps', COUNT(*) FROM "event_rsvps"
UNION ALL
SELECT 'custom_fields', COUNT(*) FROM "custom_fields"
UNION ALL
SELECT 'custom_field_responses', COUNT(*) FROM "custom_field_responses"
UNION ALL
SELECT 'event_templates', COUNT(*) FROM "event_templates"
UNION ALL
SELECT 'email_preferences', COUNT(*) FROM "email_preferences"
UNION ALL
SELECT 'organization_profile', COUNT(*) FROM "organization_profile";

-- 2. Disable foreign key constraints temporarily
SET session_replication_role = replica;

-- 3. Delete all data in the correct order (children first, then parents)
\echo 'Deleting all data...'

-- Delete junction/relationship tables first
DELETE FROM "user_organizations";
DELETE FROM "event_rsvps"; 
DELETE FROM "custom_field_responses";

-- Delete child tables
DELETE FROM "custom_fields";
DELETE FROM "event_templates";
DELETE FROM "events";
DELETE FROM "email_preferences";
DELETE FROM "organization_profile";

-- Delete parent tables last
DELETE FROM "user";
DELETE FROM "organization";

-- 4. Reset all sequences to start from 1
\echo 'Resetting sequences...'
SELECT setval('"user_id_seq"', 1, false);
SELECT setval('"organization_id_seq"', 1, false);
SELECT setval('"events_id_seq"', 1, false);
SELECT setval('"event_templates_id_seq"', 1, false);
SELECT setval('"custom_fields_id_seq"', 1, false);
SELECT setval('"custom_field_responses_id_seq"', 1, false);

-- 5. Re-enable foreign key constraints
SET session_replication_role = DEFAULT;

-- 6. Verify the cleanup
\echo 'Verification - all counts should be 0:'
SELECT 'users' as table_name, COUNT(*) as count FROM "user"
UNION ALL
SELECT 'organizations', COUNT(*) FROM "organization"
UNION ALL  
SELECT 'events', COUNT(*) FROM "events"
UNION ALL
SELECT 'user_organizations', COUNT(*) FROM "user_organizations"
UNION ALL
SELECT 'event_rsvps', COUNT(*) FROM "event_rsvps"
UNION ALL
SELECT 'custom_fields', COUNT(*) FROM "custom_fields"
UNION ALL
SELECT 'custom_field_responses', COUNT(*) FROM "custom_field_responses"
UNION ALL
SELECT 'event_templates', COUNT(*) FROM "event_templates"
UNION ALL
SELECT 'email_preferences', COUNT(*) FROM "email_preferences"
UNION ALL
SELECT 'organization_profile', COUNT(*) FROM "organization_profile";

\echo 'Database reset complete!'
