-- Event Cancellation System Migration
-- Add cancellation fields to event table

ALTER TABLE event ADD COLUMN is_cancelled BOOLEAN DEFAULT FALSE;
ALTER TABLE event ADD COLUMN cancelled_at TIMESTAMP NULL;
ALTER TABLE event ADD COLUMN cancelled_by INTEGER NULL;
ALTER TABLE event ADD COLUMN cancellation_reason TEXT NULL;
ALTER TABLE event ADD COLUMN cancellation_notification_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE event ADD CONSTRAINT fk_event_cancelled_by FOREIGN KEY (cancelled_by) REFERENCES "user"(id);

-- Verify the changes
\d event;
