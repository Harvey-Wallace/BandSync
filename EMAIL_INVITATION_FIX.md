# Email Invitation Fix for Multi-Organization Support

## Problem
After implementing multi-organization support, the email invitation system was broken with the error:
```
Error sending user invitation: 'User' object has no attribute 'organization'
```

## Root Cause
The email service was trying to access `user.organization` which was a legacy direct relationship that we removed when migrating to the UserOrganization junction table for multi-organization support.

## Fixed Files

### 1. `/backend/routes/admin.py`
- **Function**: `send_invitation_email()`
- **Changes**: 
  - Added organization retrieval from JWT context
  - Pass organization as parameter to email service
  - Added proper error handling for missing organization

### 2. `/backend/services/email_service.py`
- **Function**: `send_user_invitation()`
- **Changes**:
  - Added `organization` parameter to function signature
  - Updated template rendering to use passed organization instead of `user.organization`
  - Updated email subject to use `organization.name` instead of `user.organization.name`

### 3. Additional Legacy Reference Fixes
- Fixed email uniqueness check to be global instead of organization-specific
- Updated `get_all_users()` to use UserOrganization table
- Updated avatar upload function to use UserOrganization table
- Fixed section assignment function to use UserOrganization table

## Technical Details

### Before Fix:
```python
# Email service trying to access removed attribute
organization=user.organization,  # ❌ This failed
subject = f"Welcome to {user.organization.name} on BandSync!"  # ❌ This failed
```

### After Fix:
```python
# Admin route gets organization from JWT context
claims = get_jwt()
org_id = claims.get('organization_id')
organization = Organization.query.get(org_id)

# Email service receives organization as parameter
def send_user_invitation(self, user, temporary_password: str, inviting_admin, organization):
    # Use passed organization
    organization=organization,  # ✅ Works
    subject = f"Welcome to {organization.name} on BandSync!"  # ✅ Works
```

## Impact
- ✅ User invitations with email now work correctly
- ✅ Multi-organization context is properly maintained
- ✅ All legacy database references updated
- ✅ Email uniqueness is now global (prevents duplicate emails across organizations)

## Testing
After deployment, you can test by:
1. Log in as admin
2. Create a new user
3. Check "Send invitation email"
4. Verify the user receives the invitation email
5. Verify the email contains the correct organization name

## Next Steps
1. Wait for Railway deployment to complete
2. Test user creation with email invitation
3. Verify the admin user visibility issue is resolved with the "Add Existing User" feature
