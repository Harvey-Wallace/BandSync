
-- Add admin attendance columns to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_admin_attendance_reports BOOLEAN DEFAULT TRUE;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS admin_attendance_report_timing INTEGER DEFAULT 120;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS admin_attendance_report_unit VARCHAR(20) DEFAULT 'minutes';
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_admin_rsvp_changes BOOLEAN DEFAULT TRUE;

-- Create admin attendance tables
CREATE TABLE IF NOT EXISTS admin_attendance_report (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id),
    organization_id INTEGER REFERENCES organization(id),
    report_data JSONB,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_rsvp_change_notification (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id),
    user_id INTEGER REFERENCES "user"(id),
    organization_id INTEGER REFERENCES organization(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    change_reason VARCHAR(255),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

