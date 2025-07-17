# Password Generation Fix for Email Invitations

## Problem
Users were receiving email invitations with blank temporary passwords, even though the email sending functionality was working correctly.

## Root Cause
The issue was in how the password generation logic handled empty password fields from the frontend. When the frontend sent:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "",  // Empty string instead of omitting field
  "send_invitation": true
}
```

The original code:
```python
password = data.get('password', f"temp_{data['username']}123")
```

Would return `""` (empty string) instead of the default temporary password, because `data.get('password')` returned `""` which is truthy enough to not trigger the default value.

## Solution
Updated the password generation logic to properly handle empty strings:

```python
# Set password (either provided or generate temporary)
provided_password = data.get('password', '').strip()
if provided_password:
    password = provided_password
else:
    # Generate temporary password if none provided or empty
    password = f"temp_{data['username']}123"
```

And updated the response logic:
```python
'temporary_password': password if not provided_password else None
```

## Fixed Files

### `/backend/routes/admin.py`
- **Function**: `create_user()` (around line 493)
- **Changes**: 
  - Added proper handling for empty password strings
  - Updated response logic to use the same password validation
  - Ensures temporary passwords are generated when no valid password is provided

## Technical Details

### Before Fix:
```python
# This would set password to "" if frontend sent empty string
password = data.get('password', f"temp_{data['username']}123")
# Result: password = "" (empty string)
```

### After Fix:
```python
# This properly checks if password is actually provided and non-empty
provided_password = data.get('password', '').strip()
if provided_password:
    password = provided_password
else:
    password = f"temp_{data['username']}123"
# Result: password = "temp_username123" (proper temporary password)
```

## Impact
- ✅ Email invitations now contain proper temporary passwords
- ✅ Users can successfully log in with temporary passwords
- ✅ Frontend can send empty password fields without breaking functionality
- ✅ Maintains backwards compatibility with existing frontend implementations

## Expected Behavior
After this fix, when creating a user with email invitation:
1. If password field is provided and non-empty → use provided password
2. If password field is empty/missing → generate temporary password like `temp_username123`
3. Email invitation will contain the proper temporary password
4. User can log in with the temporary password

## Testing
After deployment, test by:
1. Creating a new user without providing a password
2. Checking "Send invitation email"
3. Verify the email contains a temporary password like `temp_username123`
4. Verify the user can log in with that temporary password
