-- Migration script to create UserOrganization entries for existing users
-- This fixes the issue where cancellation notifications weren't being sent 
-- because users weren't properly linked to organizations

-- Create UserOrganization entries for users who don't have them
INSERT INTO user_organizations (user_id, organization_id, role, section_id, is_active, joined_at)
SELECT 
    u.id AS user_id,
    u.organization_id,
    u.role,
    u.section_id,
    true AS is_active,
    NOW() AS joined_at
FROM "user" u
WHERE u.organization_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM user_organizations uo 
    WHERE uo.user_id = u.id 
    AND uo.organization_id = u.organization_id
);

-- Update users to have current_organization_id and primary_organization_id
UPDATE "user" 
SET 
    current_organization_id = organization_id,
    primary_organization_id = organization_id
WHERE organization_id IS NOT NULL 
AND (current_organization_id IS NULL OR primary_organization_id IS NULL);

-- Verify the migration
SELECT 
    'Users with organization_id' AS description,
    COUNT(*) AS count
FROM "user" 
WHERE organization_id IS NOT NULL

UNION ALL

SELECT 
    'Active UserOrganizations' AS description,
    COUNT(*) AS count
FROM user_organizations 
WHERE is_active = true;

-- Show sample of created UserOrganizations
SELECT 
    uo.id,
    u.username,
    u.email,
    o.name AS organization_name,
    uo.role,
    uo.is_active
FROM user_organizations uo
JOIN "user" u ON uo.user_id = u.id
JOIN organization o ON uo.organization_id = o.id
WHERE uo.is_active = true
ORDER BY uo.id
LIMIT 10;
