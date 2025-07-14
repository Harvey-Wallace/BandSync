from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from models import db, User, Organization, UserOrganization

org_bp = Blueprint('organization', __name__)

@org_bp.route('/switch', methods=['POST'])
@jwt_required()
def switch_organization():
    """Switch user's current organization context"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'organization_id' not in data:
        return jsonify({'error': 'organization_id is required'}), 400
    
    org_id = data['organization_id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify user has access to this organization
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id, 
        is_active=True
    ).first()
    
    if not user_org:
        return jsonify({'error': 'Access denied to this organization'}), 403
    
    # Switch organization
    user.current_organization_id = org_id
    db.session.commit()
    
    # Get organization details
    org = Organization.query.get(org_id)
    
    # Create new token with updated organization context
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user_org.role,  # Role in the new organization
            'organization_id': org_id,
            'organization': org.name if org else None
        }
    )
    
    return jsonify({
        'msg': 'Organization switched successfully',
        'access_token': access_token,
        'organization': {
            'id': org.id,
            'name': org.name,
            'logo_url': org.logo_url
        },
        'role': user_org.role
    })

@org_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_organizations():
    """Get all organizations the current user belongs to"""
    user_id = get_jwt_identity()
    
    # Get all active organizations for this user
    user_orgs = db.session.query(UserOrganization, Organization).join(
        Organization, UserOrganization.organization_id == Organization.id
    ).filter(
        UserOrganization.user_id == user_id,
        UserOrganization.is_active == True
    ).all()
    
    organizations = []
    for user_org, org in user_orgs:
        organizations.append({
            'id': org.id,
            'name': org.name,
            'logo_url': org.logo_url,
            'theme_color': org.theme_color,
            'role': user_org.role,
            'joined_at': user_org.joined_at.isoformat() if user_org.joined_at else None
        })
    
    return jsonify({
        'organizations': organizations,
        'count': len(organizations)
    })

@org_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_organization():
    """Get the user's current organization context"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.current_organization_id:
        return jsonify({'error': 'No current organization set'}), 404
    
    org = Organization.query.get(user.current_organization_id)
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=user.current_organization_id
    ).first()
    
    return jsonify({
        'organization': {
            'id': org.id,
            'name': org.name,
            'logo_url': org.logo_url,
            'theme_color': org.theme_color
        },
        'role': user_org.role if user_org else user.role
    })
