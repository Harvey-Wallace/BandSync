from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import RSVP, User

rsvps_bp = Blueprint('rsvps', __name__)

@rsvps_bp.route('/<int:event_id>/rsvps', methods=['GET'])
@jwt_required()
def get_event_rsvps(event_id):
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    org_id = claims.get('organization_id')
    # Only allow access to RSVPs for events in the user's org
    from models import Event
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Not found'}), 404
    rsvps = RSVP.query.filter_by(event_id=event_id).all()
    summary = {'Yes': [], 'No': [], 'Maybe': []}
    for r in rsvps:
        user = User.query.get(r.user_id)
        if user and user.organization_id == org_id:
            # Return both username and full name for better display
            user_info = {
                'username': user.username,
                'name': user.name or user.username,  # Fallback to username if name is empty
                'display_name': user.name or user.username,  # Convenient display name
                'section_id': user.section_id,
                'section_name': user.section.name if user.section else None
            }
            # Normalize the status to proper case to handle any legacy data
            status = r.status
            if status in ['yes', 'no', 'maybe']:
                status = status.capitalize()
            elif status not in ['Yes', 'No', 'Maybe']:
                status = 'No'  # Default fallback
            
            summary[status].append(user_info)
    return jsonify(summary)
