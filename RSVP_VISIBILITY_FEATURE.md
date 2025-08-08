# RSVP Visibility Control Feature

## Overview
This feature allows admin users to control whether regular members can see other members' RSVP responses to events. This provides privacy control for organizations that prefer to keep individual attendance information private.

## Database Changes
- Added `members_can_view_rsvp_status` column to the `organization` table
- Default value: `TRUE` (maintains existing behavior)
- Type: Boolean

## API Endpoints

### Get RSVP Visibility Setting
```
GET /api/organizations/settings/rsvp-visibility
```
**Authorization:** JWT token required
**Returns:** Current organization's RSVP visibility setting

**Response:**
```json
{
  "organization_id": 1,
  "organization_name": "Example Band",
  "members_can_view_rsvp_status": true
}
```

### Update RSVP Visibility Setting
```
PUT /api/organizations/settings/rsvp-visibility
```
**Authorization:** JWT token required, Admin role only
**Body:**
```json
{
  "members_can_view_rsvp_status": false
}
```

**Response:**
```json
{
  "msg": "RSVP visibility setting updated successfully",
  "organization_id": 1,
  "organization_name": "Example Band",
  "members_can_view_rsvp_status": false,
  "updated_by": 123
}
```

## Behavior Changes

### When RSVP Visibility is Enabled (Default)
- Admin users: See all RSVP details including names and responses
- Regular members: See all RSVP details including names and responses
- Behavior unchanged from before

### When RSVP Visibility is Disabled
- Admin users: Continue to see all RSVP details (full administrative access)
- Regular members: 
  - See aggregate counts (total Yes/No/Maybe responses)
  - See only their own individual RSVP response
  - Cannot see other members' names or individual responses
  - Receive privacy message explaining the limitation

## Event API Response Changes

The `/api/events/` endpoint now includes:

1. **`can_view_details`** field indicating if the current user can see detailed RSVPs
2. **`privacy_message`** field (when applicable) explaining privacy restrictions
3. **Filtered `responses`** array based on privacy settings

### Example Response for Regular Member (Privacy Disabled)
```json
{
  "rsvp_stats": {
    "total_responses": 15,
    "total_users": 20,
    "yes_count": 12,
    "no_count": 2,
    "maybe_count": 1,
    "no_response_count": 5,
    "can_view_details": false,
    "privacy_message": "Individual RSVP details are private. Only totals and your own response are shown.",
    "responses": [
      {
        "user_id": 123,
        "name": "Current User",
        "status": "Yes",
        "section": "Trumpets"
      }
    ]
  }
}
```

## Migration

### Automatic Migration
The feature includes automatic database migration that:
1. Runs on Railway deployment when the app starts
2. Adds the new column if it doesn't exist
3. Sets default value to `TRUE` for all existing organizations
4. Handles timeouts gracefully and continues app startup

### Migration Files
- `railway_rsvp_visibility_migration.py` - Railway-specific PostgreSQL migration
- `add_rsvp_visibility_setting.py` - Local SQLite migration
- `railway_startup.sh` - Startup script with migration integration

## Frontend Integration

To integrate this feature in the frontend:

1. **Admin Settings Page:**
   - Add toggle switch for "Allow members to see other members' RSVP responses"
   - Use the PUT endpoint to update the setting

2. **Event List/Detail Pages:**
   - Check the `can_view_details` field in RSVP stats
   - Show/hide detailed member responses accordingly
   - Display privacy message when applicable

3. **User Experience:**
   - When privacy is enabled: Show full RSVP list
   - When privacy is disabled: Show only counts + user's own response
   - Clear messaging about privacy settings

## Security Notes

- Only Admin users can modify the privacy setting
- Regular members always see aggregate counts (not completely hidden)
- Users always see their own RSVP response regardless of privacy setting
- Super admin users have full access regardless of organization settings

## Deployment

This feature is automatically deployed via Railway when:
1. Code is pushed to the GitHub repository
2. Railway detects the changes and triggers a new deployment
3. The startup script runs the migration before starting the Flask app
4. All existing organizations default to allowing RSVP visibility (no breaking changes)
