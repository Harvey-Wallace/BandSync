# Admin Attendance Notification System

## Overview
The Admin Attendance Notification System provides comprehensive event attendance tracking and notifications for band administrators. This system automatically sends attendance reports before events and notifies admins of any RSVP changes that occur after the report is sent.

## Features

### 1. Pre-Event Attendance Reports
- **Automatic Timing**: Reports are sent at configurable intervals before events (30 minutes to 1 day)
- **Detailed Breakdown**: Shows attendance by section with visual indicators
- **Summary Stats**: Quick overview of total Yes/No/Maybe/No Response counts
- **Member Details**: Lists all members with their RSVP status and section

### 2. RSVP Change Notifications
- **Post-Report Tracking**: Monitors RSVP changes after attendance report is sent
- **Instant Notifications**: Admins receive immediate notifications when members change their RSVP
- **Change Details**: Shows what the member changed from and to, with timestamps

### 3. Admin Preferences
- **Configurable Timing**: Choose when to receive attendance reports (30min, 1hr, 1.5hr, 2hr, 5hr, 1 day)
- **Toggle Controls**: Enable/disable attendance reports and change notifications independently
- **Admin-Only Access**: Only users with admin role can access these preferences

## Technical Implementation

### Database Schema
```sql
-- Admin attendance reports tracking
CREATE TABLE admin_attendance_reports (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id),
    organization_id INTEGER REFERENCES organization(id),
    report_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_yes INTEGER DEFAULT 0,
    total_no INTEGER DEFAULT 0,
    total_maybe INTEGER DEFAULT 0,
    total_no_response INTEGER DEFAULT 0
);

-- RSVP change notifications
CREATE TABLE admin_rsvp_change_notifications (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id),
    user_id INTEGER REFERENCES user(id),
    organization_id INTEGER REFERENCES organization(id),
    previous_status VARCHAR(10),
    new_status VARCHAR(10) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notification_sent BOOLEAN DEFAULT FALSE
);

-- User preference columns
ALTER TABLE user ADD COLUMN email_admin_attendance_reports BOOLEAN DEFAULT TRUE;
ALTER TABLE user ADD COLUMN admin_attendance_report_timing INTEGER DEFAULT 120;
ALTER TABLE user ADD COLUMN admin_attendance_report_unit VARCHAR(20) DEFAULT 'minutes';
ALTER TABLE user ADD COLUMN email_admin_rsvp_changes BOOLEAN DEFAULT TRUE;
```

### Backend Components

#### AdminAttendanceService
- **check_and_send_attendance_reports()**: Main function to check for events needing reports
- **track_rsvp_change()**: Records RSVP changes and triggers notifications
- **_send_attendance_report()**: Sends detailed HTML attendance reports
- **_send_rsvp_change_notification()**: Sends change notifications to admins

#### Background Jobs
- **attendance_check.py**: Scheduler script to run every 5 minutes
- Integrates with existing RSVP system to track changes
- Automatic email generation with professional HTML formatting

#### API Endpoints
- `GET /email/preferences` - Get user preferences (includes admin settings)
- `PUT /email/preferences` - Update preferences (validates admin access)
- `GET /email/admin/attendance-timing-options` - Get timing options for admins

### Frontend Components

#### Email Preferences Page
- **Admin Section**: Appears only for admin users
- **Timing Dropdown**: Pre-defined options (30min, 1hr, 1.5hr, 2hr, 5hr, 1 day)
- **Toggle Controls**: Individual on/off switches for each notification type
- **Real-time Validation**: Form validation and error handling

## Usage Instructions

### For Administrators

1. **Setup Preferences**:
   - Navigate to Email Preferences page
   - Locate "Admin Attendance Notifications" section
   - Enable "Event Attendance Reports"
   - Select timing (how far before events to receive reports)
   - Enable "RSVP Change Notifications" if desired

2. **Reading Attendance Reports**:
   - Reports arrive at configured time before events
   - Shows total counts with color coding (Green=Yes, Red=No, Yellow=Maybe, Gray=No Response)
   - Section-by-section breakdown with member names
   - Lists members who haven't responded

3. **RSVP Change Notifications**:
   - Receive instant notifications when members change RSVPs
   - Shows member name, event, and what changed
   - Only sent for changes after attendance report was sent

### For System Administrators

1. **Deployment**:
   - Run database migration: `python3 migrate_admin_attendance.py`
   - Deploy updated backend code
   - Set up cron job for `backend/jobs/attendance_check.py` (every 5 minutes)

2. **Monitoring**:
   - Check EmailLog table for delivery status
   - Monitor background job execution
   - Review AdminAttendanceReport table for sent reports

## Email Templates

### Attendance Report Email
- Professional HTML layout with BandSync branding
- Summary statistics with visual indicators
- Section-organized member lists
- Color-coded RSVP statuses
- Event details and location information

### RSVP Change Notification
- Compact format highlighting the change
- Member name and event details
- Before/after status with icons
- Timestamp of the change

## Configuration Options

### Timing Options
- **30 minutes**: Last-minute attendance check
- **1 hour**: Standard pre-event notification
- **1.5 hours**: Extended preparation time
- **2 hours**: Early notification for complex events
- **5 hours**: Half-day advance notice
- **1 day**: Full day preparation

### Customization
- Email templates can be customized in `AdminAttendanceService`
- Timing options can be modified in `get_timing_options()`
- Background job frequency can be adjusted in cron configuration

## Benefits

1. **Improved Event Planning**: Admins know attendance in advance
2. **Better Member Management**: Track who's not responding
3. **Real-time Updates**: Instant notifications of changes
4. **Reduced Manual Work**: Automated report generation
5. **Professional Communication**: Well-formatted email reports
6. **Flexible Configuration**: Customizable timing and preferences

## Future Enhancements

1. **Organization-level Settings**: Configure timing per organization
2. **Advanced Filters**: Filter reports by section or event type
3. **Mobile Notifications**: Push notifications for urgent changes
4. **Analytics Integration**: Track attendance patterns over time
5. **Custom Templates**: User-customizable email templates
6. **Multiple Recipients**: Send to multiple admin roles
