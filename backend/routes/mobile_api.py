from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Organization, UserOrganization, Section

mobile_api_bp = Blueprint('mobile_api', __name__)

@mobile_api_bp.route('/', methods=['GET'])
@jwt_required()
def get_organization():
    """Get organization details for mobile app - /api/organization"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    # Get organization from JWT claims first (current context)
    org_id = claims.get('organization_id')
    
    if not org_id:
        # Fallback to user's default organization
        user = User.query.get(user_id)
        if user and user.current_organization_id:
            org_id = user.current_organization_id
        else:
            return jsonify({'error': 'No current organization set'}), 404
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Build organization response for mobile app
    return jsonify({
        'id': org.id,
        'name': org.name,
        'logo_url': org.logo_url,
        'description': org.rehearsal_address or '',  # Use rehearsal address as description
        'created_at': org.created_at.isoformat() if org.created_at else None,
        'settings': {
            'theme_color': org.theme_color or '#007bff',
            'contact_phone': org.contact_phone,
            'contact_email': org.contact_email,
            'website': org.website,
            'facebook_url': org.facebook_url,
            'instagram_url': org.instagram_url,
            'twitter_url': org.twitter_url,
            'tiktok_url': org.tiktok_url
        }
    })


@mobile_api_bp.route('/members/', methods=['GET'])
@jwt_required()
def get_organization_members():
    """Get organization members for mobile app - /api/organization/members/"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    # Get organization from JWT claims first (current context)
    org_id = claims.get('organization_id')
    
    if not org_id:
        # Fallback to user's default organization
        user = User.query.get(user_id)
        if user and user.current_organization_id:
            org_id = user.current_organization_id
        else:
            return jsonify({'error': 'No current organization set'}), 404
    
    # Get all active members of this organization
    members_query = db.session.query(User, UserOrganization, Section).outerjoin(
        UserOrganization, User.id == UserOrganization.user_id
    ).outerjoin(
        Section, UserOrganization.section_id == Section.id
    ).filter(
        UserOrganization.organization_id == org_id,
        UserOrganization.is_active == True
    ).all()
    
    members = []
    for user, user_org, section in members_query:
        # Fallback to legacy section if no UserOrganization section
        section_name = None
        if section:
            section_name = section.name
        elif user.section_id:
            legacy_section = Section.query.get(user.section_id)
            if legacy_section:
                section_name = legacy_section.name
        
        members.append({
            'id': user.id,
            'name': user.name or user.username,
            'username': user.username,
            'section': section_name or 'Unassigned',
            'role': user_org.role if user_org else 'Member',
            'avatar_url': user.avatar_url
        })
    
    # Sort members by section, then by name
    members.sort(key=lambda m: (m['section'] or 'ZZZ', m['name'] or m['username']))
    
    return jsonify({
        'members': members
    })
