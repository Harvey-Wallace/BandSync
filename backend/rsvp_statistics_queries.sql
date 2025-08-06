-- Enhanced Events Endpoint with RSVP Statistics
-- This query shows how the RSVP statistics are calculated for each event

-- Example query to get RSVP statistics for all events in an organization
SELECT 
    e.id as event_id,
    e.title,
    e.date,
    COUNT(r.id) as total_responses,
    (
        SELECT COUNT(DISTINCT u.id) 
        FROM user u 
        LEFT JOIN user_organizations uo ON u.id = uo.user_id 
        WHERE (u.organization_id = :org_id OR (uo.organization_id = :org_id AND uo.is_active = TRUE))
    ) as total_users,
    SUM(CASE WHEN r.status = 'Yes' THEN 1 ELSE 0 END) as yes_count,
    SUM(CASE WHEN r.status = 'No' THEN 1 ELSE 0 END) as no_count,
    SUM(CASE WHEN r.status = 'Maybe' THEN 1 ELSE 0 END) as maybe_count,
    (
        SELECT COUNT(DISTINCT u.id) 
        FROM user u 
        LEFT JOIN user_organizations uo ON u.id = uo.user_id 
        WHERE (u.organization_id = :org_id OR (uo.organization_id = :org_id AND uo.is_active = TRUE))
    ) - COUNT(r.id) as no_response_count
FROM event e
LEFT JOIN rsvp r ON e.id = r.event_id
LEFT JOIN user u ON r.user_id = u.id
LEFT JOIN user_organizations uo ON u.id = uo.user_id
WHERE e.organization_id = :org_id
    AND e.is_template = FALSE
    AND (
        u.organization_id = :org_id 
        OR (uo.organization_id = :org_id AND uo.is_active = TRUE)
        OR r.id IS NULL
    )
GROUP BY e.id, e.title, e.date
ORDER BY e.date ASC;

-- Performance Notes:
-- 1. The current implementation uses individual queries per event for simplicity
-- 2. For better performance with many events, consider using a single query like above
-- 3. Add database indexes on commonly queried fields:

-- Recommended indexes for optimal performance:
CREATE INDEX IF NOT EXISTS idx_rsvp_event_user ON rsvp(event_id, user_id);
CREATE INDEX IF NOT EXISTS idx_user_organization ON user(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_organizations_active ON user_organizations(organization_id, is_active, user_id);
CREATE INDEX IF NOT EXISTS idx_event_organization_template ON event(organization_id, is_template);

-- Query to verify RSVP statistics for a specific event:
SELECT 
    'Event: ' || e.title as info,
    'Total Users in Org: ' || (
        SELECT COUNT(DISTINCT u.id) 
        FROM user u 
        LEFT JOIN user_organizations uo ON u.id = uo.user_id 
        WHERE (u.organization_id = e.organization_id OR (uo.organization_id = e.organization_id AND uo.is_active = TRUE))
    ) as total_users,
    'Total Responses: ' || COUNT(r.id) as total_responses,
    'Yes: ' || SUM(CASE WHEN r.status = 'Yes' THEN 1 ELSE 0 END) as yes_count,
    'No: ' || SUM(CASE WHEN r.status = 'No' THEN 1 ELSE 0 END) as no_count,
    'Maybe: ' || SUM(CASE WHEN r.status = 'Maybe' THEN 1 ELSE 0 END) as maybe_count
FROM event e
LEFT JOIN rsvp r ON e.id = r.event_id
LEFT JOIN user u ON r.user_id = u.id
LEFT JOIN user_organizations uo ON u.id = uo.user_id
WHERE e.id = :event_id
    AND (
        u.organization_id = e.organization_id 
        OR (uo.organization_id = e.organization_id AND uo.is_active = TRUE)
        OR r.id IS NULL
    )
GROUP BY e.id, e.title;
