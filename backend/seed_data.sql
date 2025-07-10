
-- Create test organizations
INSERT INTO organization (id, name) VALUES
(1, 'Test Band'),
(2, 'Second Band');

-- Create test users (now with organization_id)
INSERT INTO "user" (username, email, password_hash, role, organization_id) VALUES
('admin', 'admin@bandsync.com', '$pbkdf2-sha256$29000$testadminhash', 'Admin', 1),
('member1', 'member1@bandsync.com', '$pbkdf2-sha256$29000$testmemberhash', 'Member', 1),
('admin2', 'admin2@second.com', '$pbkdf2-sha256$29000$testadmin2hash', 'Admin', 2);


-- Create test events (now with organization_id)
INSERT INTO event (title, description, date, location, organization_id) VALUES
('First Rehearsal', 'Season opener rehearsal', '2025-08-01T19:00:00', 'Band Hall', 1),
('Concert', 'Annual summer concert', '2025-08-15T19:30:00', 'Town Square', 1),
('Second Org Event', 'Second org only', '2025-09-01T19:00:00', 'Second Hall', 2);


-- Create test RSVPs
INSERT INTO rsvp (user_id, event_id, status) VALUES
(1, 1, 'Yes'),
(2, 1, 'Maybe'),
(1, 2, 'No'),
(3, 3, 'Yes');
