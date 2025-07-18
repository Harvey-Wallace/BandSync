from flask_jwt_extended import get_jwt
from models import User, Organization

def is_super_admin(user_id):
    """Check if user is a Super Admin"""
    user = User.query.get(user_id)
    return user and user.super_admin

def get_user_organizations(user_id):
    """Get all organizations for a user, considering Super Admin status"""
    user = User.query.get(user_id)
    if not user:
        return []
    
    if user.super_admin:
        # Super Admin has access to all organizations
        return Organization.query.all()
    
    # Regular user - get their organizations from UserOrganization table
    from models import UserOrganization
    user_orgs = UserOrganization.query.filter_by(user_id=user_id).all()
    return [uo.organization for uo in user_orgs]

def can_access_organization(user_id, organization_id):
    """Check if user can access a specific organization"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    if user.super_admin:
        # Super Admin can access any organization
        return True
    
    # Check if user belongs to the organization
    from models import UserOrganization
    user_org = UserOrganization.query.filter_by(
        user_id=user_id,
        organization_id=organization_id
    ).first()
    
    return user_org is not None

def get_admin_context(user_id):
    """Get admin context for a user"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    jwt_claims = get_jwt()
    
    return {
        'user_id': user_id,
        'username': user.username,
        'is_super_admin': user.super_admin,
        'current_organization_id': jwt_claims.get('organization_id'),
        'jwt_role': jwt_claims.get('role'),
        'accessible_organizations': get_user_organizations(user_id)
    }
