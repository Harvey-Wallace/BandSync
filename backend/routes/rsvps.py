from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import RSVP, User, UserOrganization

rsvps_bp = Blueprint('rsvps', __name__)

@rsvps_bp.route('/<int:event_id>/rsvps', methods=['GET'])
@jwt_required()
def get_event_rsvps(event_id):
    from flask_jwt_extended import get_jwt, get_jwt_identity
    claims = get_jwt()
    org_id = claims.get('organization_id')
    user_role = claims.get('role')
    current_user_id = get_jwt_identity()
    
    # Only allow access to RSVPs for events in the user's org
    from models import Event, Organization
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Not found'}), 404
    
    # Check organization privacy setting
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'msg': 'Organization not found'}), 404
    
    # Determine if user can see detailed RSVP responses
    can_see_details = (user_role == 'Admin') or getattr(org, 'members_can_view_rsvp_status', True)
    
    rsvps = RSVP.query.filter_by(event_id=event_id).all()
    summary = {'Yes': [], 'No': [], 'Maybe': []}
    for r in rsvps:
        user = User.query.get(r.user_id)
        if user:
            # Check if user belongs to the organization (legacy field OR UserOrganization table)
            user_in_org = (user.organization_id == org_id) or \
                         UserOrganization.query.filter_by(user_id=user.id, organization_id=org_id, is_active=True).first()
            
            if user_in_org:
                # If user can't see details and this isn't their own RSVP, skip it
                if not can_see_details and str(user.id) != str(current_user_id):
                    continue
                    
                # Get section information - check UserOrganization first, then legacy User field
                section_id = None
                section_name = None
                
                # Check if user has section assigned through UserOrganization table
                user_org = UserOrganization.query.filter_by(
                    user_id=user.id, 
                    organization_id=org_id, 
                    is_active=True
                ).first()
                
                if user_org and user_org.section_id:
                    section_id = user_org.section_id
                    section_name = user_org.section.name if user_org.section else None
                elif user.section_id:
                    # Fall back to legacy User.section_id
                    section_id = user.section_id
                    section_name = user.section.name if user.section else None
                
                # Return both username and full name for better display
                user_info = {
                    'username': user.username,
                    'name': user.name or user.username,  # Fallback to username if name is empty
                    'display_name': user.name or user.username,  # Convenient display name
                    'section_id': section_id,
                    'section_name': section_name
                }
                
                # Include comments and likelihood if available
                if hasattr(r, 'comments') and r.comments:
                    user_info['comments'] = r.comments
                
                if hasattr(r, 'likelihood') and r.likelihood is not None:
                    user_info['likelihood'] = r.likelihood
                
                if hasattr(r, 'updated_at') and r.updated_at:
                    user_info['updated_at'] = r.updated_at.isoformat()
                
                # Normalize the status to proper case to handle any legacy data
                status = r.status
                if status in ['yes', 'no', 'maybe']:
                    status = status.capitalize()
                elif status not in ['Yes', 'No', 'Maybe']:
                    status = 'No'  # Default fallback
                
                summary[status].append(user_info)
    
    # Add privacy metadata to response
    result = summary.copy()
    result['_privacy'] = {
        'can_view_details': can_see_details,
        'privacy_message': None if can_see_details else "Individual RSVP details are private. Only totals and your own response are shown."
    }
    
    return jsonify(result)
