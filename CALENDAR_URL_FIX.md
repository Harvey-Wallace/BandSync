# Calendar URL Fix - Production Domain

## Problem
Calendar URLs on the Calendar Integration page were showing `localhost:5001` instead of the production domain `bandsync-production.up.railway.app`.

Example of broken URL:
```
http://localhost:5001/api/calendar/user/2/org/2/events.ics
```

## Root Cause
The calendar service was using two separate environment variables:
- `BASE_URL`: Set to `https://bandsync-production.up.railway.app` ✅
- `CALENDAR_URL`: Not set, defaulting to `http://localhost:5001` ❌

## Solution
Updated the calendar service to use the same base URL for both the main application and calendar endpoints since they're served by the same Flask application.

### Code Change
**File**: `backend/services/calendar_service.py`

**Before**:
```python
def __init__(self):
    self.base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
    self.calendar_url = os.environ.get('CALENDAR_URL', 'http://localhost:5001')
```

**After**:
```python
def __init__(self):
    self.base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
    # Calendar URLs should use the same base URL as the main application
    self.calendar_url = os.environ.get('CALENDAR_URL', self.base_url)
```

## Impact
✅ **Calendar URLs now show**: `https://bandsync-production.up.railway.app/api/calendar/user/2/org/2/events.ics`
✅ **Users can subscribe to calendars** using the correct production URLs
✅ **Google Calendar integration** will work properly
✅ **Outlook integration** will work properly
✅ **Apple Calendar integration** will work properly

## Expected URLs After Fix
- **Organization Calendar**: `https://bandsync-production.up.railway.app/api/calendar/org/2/events.ics`
- **User Calendar**: `https://bandsync-production.up.railway.app/api/calendar/user/2/org/2/events.ics`
- **Section Calendar**: `https://bandsync-production.up.railway.app/api/calendar/section/3/events.ics`
- **Public Calendar**: `https://bandsync-production.up.railway.app/api/calendar/public/2/events.ics`

## How to Test
1. Go to the Calendar Integration page
2. Check that all calendar URLs show `https://bandsync-production.up.railway.app` instead of `localhost:5001`
3. Copy a calendar URL and test it in a browser - it should return an ICS file
4. Try subscribing to a calendar in Google Calendar or Outlook

## Technical Details
- The fix maintains backward compatibility
- If `CALENDAR_URL` environment variable is explicitly set, it will still be used
- The change only affects the default fallback behavior
- All calendar endpoints are served by the same Flask application, so using the same base URL is correct

## Status
- ✅ **Fix committed and deployed**
- ✅ **No database changes required**
- ✅ **No frontend changes required**
- ✅ **Railway deployment will pick up the change automatically**
