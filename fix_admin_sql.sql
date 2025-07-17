-- Fix admin user in second organization
-- Run this SQL script on your database

-- First, let's see what organizations exist
SELECT id, name FROM organization ORDER BY id;

-- Check admin user
SELECT id, username, organization_id, role FROM "user" WHERE username = 'admin';

-- Check admin's current organization memberships
SELECT uo.user_id, uo.organization_id, uo.role, uo.is_active, u.username, o.name as org_name
FROM user_organizations uo
JOIN "user" u ON uo.user_id = u.id
JOIN organization o ON uo.organization_id = o.id
WHERE u.username = 'admin';

-- Add admin to second organization (adjust organization_id as needed)
-- Replace '2' with the actual ID of your second organization
INSERT INTO user_organizations (user_id, organization_id, role, is_active, joined_at)
SELECT 
    u.id,
    2,  -- Change this to the correct organization ID
    'Admin',
    true,
    NOW()
FROM "user" u
WHERE u.username = 'admin'
AND NOT EXISTS (
    SELECT 1 FROM user_organizations uo
    WHERE uo.user_id = u.id AND uo.organization_id = 2
);

-- Verify the fix
SELECT uo.user_id, uo.organization_id, uo.role, uo.is_active, u.username, o.name as org_name
FROM user_organizations uo
JOIN "user" u ON uo.user_id = u.id
JOIN organization o ON uo.organization_id = o.id
WHERE u.username = 'admin'
ORDER BY uo.organization_id;
