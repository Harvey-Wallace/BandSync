# BandSync Multi-Organization Support Implementation

## Overview

This document describes the implementation of multi-organization support in BandSync, allowing users to belong to multiple organizations with the same email address and switch between them.

## Key Features

### 1. Multi-Organization User Support
- Users can belong to multiple organizations with different roles
- Each user has a primary organization and current organization
- Users can switch between organizations during their session

### 2. Organization Context Management
- JWT tokens include organization context (organization_id, role)
- All API endpoints respect the current organization context
- Organization switching updates the JWT token with new context

### 3. Enhanced Login Flow
- If user belongs to multiple organizations, login returns organization selection
- User selects which organization to access during login
- Single-organization users proceed directly to dashboard

### 4. Frontend Organization Switcher
- Navbar displays current organization as a clickable badge
- Dropdown shows available organizations for switching
- Organization switching refreshes the page with new context

## Database Schema Changes

### New Tables

#### `user_organizations` (Association Table)
- `user_id` (Foreign Key to users.id)
- `organization_id` (Foreign Key to organization.id)
- `role` (String: Admin, Member, etc.)
- `created_at` (DateTime)

### Modified Tables

#### `users` Table
- Added `current_organization_id` (Foreign Key to organization.id)
- Added `primary_organization_id` (Foreign Key to organization.id)
- Maintained `organization_id` for backward compatibility

## Backend Implementation

### 1. Updated Models (`models.py`)

```python
class UserOrganization(db.Model):
    """Association table for many-to-many user-organization relationship"""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), primary_key=True)
    role = db.Column(db.String(50), nullable=False, default='Member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    # ... existing fields ...
    current_organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    primary_organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    
    # Relationships
    organizations = db.relationship('Organization', secondary='user_organizations', 
                                   back_populates='users')
    current_organization = db.relationship('Organization', foreign_keys=[current_organization_id])
    primary_organization = db.relationship('Organization', foreign_keys=[primary_organization_id])
```

### 2. Enhanced Authentication (`auth/routes.py`)

#### Multi-Organization Login
```python
@auth_bp.route('/login', methods=['POST'])
def login():
    # ... authentication logic ...
    
    # Get all organizations user belongs to
    user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
    
    # If user belongs to multiple organizations and no specific org requested
    if len(user_orgs) > 1 and not requested_org_id:
        return jsonify({
            'multiple_organizations': True,
            'organizations': [
                {
                    'id': uo.organization_id,
                    'name': uo.organization.name,
                    'role': uo.role
                } for uo in user_orgs
            ]
        })
```

### 3. Organization Management API (`routes/organizations.py`)

#### Switch Organization
```python
@organizations_bp.route('/switch', methods=['POST'])
@jwt_required()
def switch_organization():
    # Validate user membership
    # Update current organization
    # Create new JWT token with updated context
    # Return new token and organization info
```

#### Available Organizations
```python
@organizations_bp.route('/available', methods=['GET'])
@jwt_required()
def available_organizations():
    # Return all organizations user belongs to
    # Include role information for each organization
```

#### Current Organization
```python
@organizations_bp.route('/current', methods=['GET'])
@jwt_required()
def current_organization():
    # Return current organization context from JWT
    # Include role and organization details
```

## Frontend Implementation

### 1. Organization Context Provider (`contexts/OrganizationContext.js`)

```javascript
export const OrganizationProvider = ({ children }) => {
  const [currentOrganization, setCurrentOrganization] = useState(null);
  const [availableOrganizations, setAvailableOrganizations] = useState([]);
  
  const switchOrganization = async (organizationId) => {
    // Call API to switch organization
    // Update localStorage with new token
    // Refresh page to update all components
  };
  
  // ... other methods ...
};
```

### 2. Organization Switcher Component (`components/OrganizationSwitcher.js`)

```javascript
function OrganizationSwitcher() {
  const { currentOrganization, availableOrganizations, switchOrganization } = useOrganization();
  
  // Render organization badge with dropdown
  // Handle organization switching
  // Show loading states and error handling
}
```

### 3. Enhanced Login Page (`pages/LoginPage.js`)

```javascript
// Handle multi-organization login flow
if (res.data.multiple_organizations && !selectedOrgId) {
  setMultipleOrgs(res.data.organizations);
  return;
}

// Show organization selection UI
// Allow user to select organization before proceeding
```

### 4. Updated Navbar (`components/Navbar.js`)

```javascript
// Import and use OrganizationSwitcher
import OrganizationSwitcher from './OrganizationSwitcher';
import { useOrganization } from '../contexts/OrganizationContext';

// Replace static organization display with dynamic switcher
<OrganizationSwitcher />
```

## Migration Process

### 1. Database Migration (`migrations/add_multi_organization.py`)

```python
def migrate():
    # Create user_organizations table
    # Add current_organization_id and primary_organization_id to users
    # Migrate existing data to new structure
    # Update sequences and constraints
```

### 2. Data Migration Strategy

1. **Create Association Table**: Set up user_organizations table
2. **Migrate Existing Data**: Copy existing user-organization relationships
3. **Update User Records**: Set current and primary organization IDs
4. **Preserve Backward Compatibility**: Keep existing organization_id field

## Testing

### 1. Backend API Tests

```bash
# Test multi-organization login
python test_multi_org.py

# Test complete flow
python test_complete_flow.py
```

### 2. Frontend Testing

1. Login with multi-organization user
2. Select organization from login screen
3. Verify organization switcher in navbar
4. Test organization switching
5. Verify context updates across the application

## Usage Examples

### 1. User Belongs to Multiple Organizations

```json
// Login response
{
  "multiple_organizations": true,
  "organizations": [
    {"id": 1, "name": "Demo Organization", "role": "Admin"},
    {"id": 2, "name": "Second Band", "role": "Member"}
  ]
}
```

### 2. Organization Switching

```json
// Switch request
POST /api/organizations/switch
{
  "organization_id": 2
}

// Switch response
{
  "access_token": "new-jwt-token",
  "organization": {"id": 2, "name": "Second Band"},
  "role": "Member"
}
```

### 3. Current Organization Context

```json
// Current organization response
{
  "organization": {"id": 1, "name": "Demo Organization"},
  "role": "Admin"
}
```

## Security Considerations

1. **JWT Token Security**: Organization context is embedded in JWT claims
2. **Role-Based Access**: API endpoints validate user roles within organization context
3. **Organization Isolation**: Data is properly isolated between organizations
4. **Membership Validation**: All organization switches validate user membership

## Future Enhancements

1. **Organization Invitations**: Allow users to be invited to organizations
2. **Role Management**: More granular role permissions within organizations
3. **Organization Settings**: Per-organization configuration and branding
4. **Audit Logging**: Track organization switches and access patterns
5. **API Rate Limiting**: Organization-specific rate limits

## Troubleshooting

### Common Issues

1. **Organization Not Found**: Verify user membership in UserOrganization table
2. **JWT Token Issues**: Check token expiration and organization context
3. **Frontend State Issues**: Ensure OrganizationProvider wraps all components
4. **Database Sequence Issues**: Run migrations in correct order

### Debug Commands

```bash
# Check database state
python check_and_setup.py

# Add test user to multiple organizations
python add_admin_to_second_band.py

# Test API endpoints
python test_multi_org.py
```

## Conclusion

The multi-organization support implementation provides a robust foundation for users to belong to multiple organizations while maintaining proper context separation and security. The implementation includes both backend API changes and frontend UI enhancements to provide a seamless user experience.
