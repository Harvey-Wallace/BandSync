-- SQL queries to check organization data on Railway
-- Run these in the Railway database console

-- Check organizations
SELECT id, name, created_at FROM organizations;

-- Check users and their organization assignments
SELECT id, name, username, email, role, organization_id FROM users;

-- Check events and their organization assignments
SELECT id, title, date, organization_id FROM events;

-- Check RSVPs
SELECT r.id, r.user_id, r.event_id, r.response, r.created_at, e.organization_id 
FROM rsvps r 
JOIN events e ON r.event_id = e.id;

-- Check if there are any analytics data issues
SELECT 
  o.name as org_name,
  COUNT(DISTINCT u.id) as total_users,
  COUNT(DISTINCT e.id) as total_events,
  COUNT(DISTINCT r.id) as total_rsvps
FROM organizations o
LEFT JOIN users u ON o.id = u.organization_id
LEFT JOIN events e ON o.id = e.organization_id
LEFT JOIN rsvps r ON e.id = r.event_id
GROUP BY o.id, o.name;
