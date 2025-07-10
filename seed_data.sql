
-- Create test organizations
INSERT INTO organization (id, name) VALUES
  (1, 'Brass Masters'),
  (2, 'Wind Ensemble');

-- Create test users (assigned to organizations)
INSERT INTO "user" (username, email, password_hash, role, organization_id) VALUES
  ('admin', 'admin@bandsync.com', 'scrypt:32768:8:1$SFvy4WQQAtetiaK4$e07a88a11935898455026d3a4844a533a95584b8bc8ed0aaf803f4a656b2d1eb0f14045d5a453749621138fad39a71a8b65e56bc02e8312b66ff68ffed3eb3ac', 'Admin', 1),
  ('member1', 'member1@bandsync.com', 'scrypt:32768:8:1$GGDSt0vvn1QUnpYt$a928de2efe7bd0628fbeb5385ab4845b3d208ea2bfbce2a6b6c877862b39ebeaca3acd3f26d4af78e14749291e94f4dda598a95524a445b17c0f986c844e07eb', 'Member', 1),
  ('windadmin', 'admin@wind.com', 'scrypt:32768:8:1$d39hFvVP3rHaTB0C$6b9520403329b132363262ac75d677f52de70f9642ad4606d6bcc13a1615a4d8749bbd21ac47afe5700d73fb7946568a293e5528c011b13d5f13403eebe582f0', 'Admin', 2),
  ('windmember', 'member@wind.com', 'scrypt:32768:8:1$5WkswzYPo9vkAUiC$4d2e754781bf6b6bf08e82b5495fd05eb9483441c8f54f1366e50ae6dbcb981405b187038302f117aa8cc92ee329716b4ed62b70fc3c3f64b667201b833e469f', 'Member', 2);


-- Create test events (assigned to organizations)
INSERT INTO event (title, description, date, location, organization_id) VALUES
  ('First Rehearsal', 'Season opener rehearsal', '2025-08-01T19:00:00', 'Band Hall', 1),
  ('Concert', 'Annual summer concert', '2025-08-15T19:30:00', 'Town Square', 1),
  ('Wind Rehearsal', 'Wind band practice', '2025-08-03T19:00:00', 'Wind Hall', 2);


-- Create test RSVPs (scoped to correct orgs/users/events)
INSERT INTO rsvp (user_id, event_id, status) VALUES
  (1, 1, 'Yes'),      -- admin (Brass Masters) RSVPs Yes to First Rehearsal
  (2, 1, 'Maybe'),    -- member1 (Brass Masters) RSVPs Maybe to First Rehearsal
  (1, 2, 'No'),       -- admin (Brass Masters) RSVPs No to Concert
  (3, 3, 'Yes'),      -- windadmin (Wind Ensemble) RSVPs Yes to Wind Rehearsal
  (4, 3, 'Maybe');    -- windmember (Wind Ensemble) RSVPs Maybe to Wind Rehearsal
