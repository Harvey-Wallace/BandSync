from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import (db, User, Organization, Event, RSVP, SubstituteRequest, 
                   CallList, Section, EventCategory)
from datetime import datetime
import uuid
from sqlalchemy import and_, or_

substitutes_bp = Blueprint('substitutes', __name__)

def get_current_user_and_org():
    """Helper function to get current user and organization from JWT"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    organization_id = claims.get('organization_id')
    
    user = User.query.get(current_user_id)
    organization = Organization.query.get(organization_id) if organization_id else None
    
    return user, organization

def is_admin(user, organization_id):
    """Check if user is admin in the specified organization"""
    if not user or not organization_id:
        return False
    return user.get_role_in_organization(organization_id) == 'Admin'

@substitutes_bp.route('/request', methods=['POST'])
@jwt_required()
def create_substitute_request():
    """Create a substitute request from an RSVP"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('event_id'):
        return jsonify({'error': 'Event ID is required'}), 400
    
    # Verify event exists and user has RSVP
    event = Event.query.filter_by(
        id=data['event_id'],
        organization_id=organization.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user has an RSVP for this event
    rsvp = RSVP.query.filter_by(
        event_id=event.id,
        user_id=user.id
    ).first()
    
    if not rsvp:
        return jsonify({'error': 'RSVP not found for this event'}), 404
    
    # Check if substitute request already exists
    existing_request = SubstituteRequest.query.filter_by(
        event_id=event.id,
        requested_by=user.id,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'Substitute request already exists for this event'}), 409
    
    # Create substitute request
    substitute_request = SubstituteRequest(
        event_id=event.id,
        requested_by=user.id,
        request_message=data.get('reason', ''),
        created_at=datetime.utcnow(),
        status='open'
    )
    
    db.session.add(substitute_request)
    db.session.commit()
    
    # Start the substitute finding process
    _process_substitute_request(substitute_request)
    
    return jsonify({
        'request_id': substitute_request.id,
        'message': 'Substitute request created successfully'
    }), 201

@substitutes_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_substitute_requests():
    """Get substitute requests for the current user or organization"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Get requests where user is the original user or potential substitute
    requests = SubstituteRequest.query.filter(
        SubstituteRequest.event.has(Event.organization_id == organization.id),
        or_(
            SubstituteRequest.requested_by == user.id,
            SubstituteRequest.filled_by == user.id
        )
    ).order_by(SubstituteRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        event = Event.query.get(req.event_id)
        requester = User.query.get(req.requested_by)
        substitute_user = User.query.get(req.filled_by) if req.filled_by else None
        
        request_data = {
            'id': req.id,
            'event': {
                'id': event.id,
                'name': event.title,
                'start_datetime': event.date.isoformat() if event.date else None,
                'end_datetime': event.end_date.isoformat() if event.end_date else None,
                'location': event.location_address
            },
            'requester': {
                'id': requester.id,
                'name': requester.name
            },
            'substitute_user': {
                'id': substitute_user.id,
                'name': substitute_user.name
            } if substitute_user else None,
            'request_message': req.request_message,
            'status': req.status,
            'created_at': req.created_at.isoformat(),
            'filled_at': req.filled_at.isoformat() if req.filled_at else None,
            'is_requester': req.requested_by == user.id,
            'is_substitute': req.filled_by == user.id
        }
        result.append(request_data)
    
    return jsonify(result)

@substitutes_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_substitutes():
    """Get available substitute requests for the current user"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Get pending substitute requests where user could be a substitute
    # (not their own requests and they're available)
    event_id = request.args.get('event_id')
    
    query = SubstituteRequest.query.filter(
        SubstituteRequest.event.has(Event.organization_id == organization.id),
        SubstituteRequest.requested_by != user.id,
        SubstituteRequest.status == 'pending'
    )
    
    if event_id:
        query = query.filter(SubstituteRequest.event_id == event_id)
    
    requests = query.order_by(SubstituteRequest.requested_at.desc()).all()
    
    result = []
    for req in requests:
        event = Event.query.get(req.event_id)
        requester = User.query.get(req.requested_by)
        
        # Check if user is already RSVP'd to this event
        existing_rsvp = RSVP.query.filter_by(
            event_id=event.id,
            user_id=user.id
        ).first()
        
        # Skip if user already has conflicting RSVP
        if existing_rsvp and existing_rsvp.response == 'yes':
            continue
        
        request_data = {
            'id': req.id,
            'event': {
                'id': event.id,
                'name': event.name,
                'start_datetime': event.date.isoformat() if event.date else None,
                'end_datetime': event.end_date.isoformat() if event.end_date else None,
                'location': event.location_address,
                'description': event.description
            },
            'requester': {
                'id': requester.id,
                'name': requester.full_name
            },
            'request_message': req.request_message,
            'created_at': req.created_at.isoformat(),
            'can_substitute': not existing_rsvp or existing_rsvp.status in ['no', 'maybe']
        }
        result.append(request_data)
    
    return jsonify(result)

@substitutes_bp.route('/accept', methods=['POST'])
@jwt_required()
def accept_substitute_request():
    """Accept a substitute request"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    if not data.get('request_id'):
        return jsonify({'error': 'Request ID is required'}), 400
    
    # Find the substitute request
    substitute_request = SubstituteRequest.query.filter_by(
        id=data['request_id'],
        status='pending'
    ).first()
    
    if not substitute_request:
        return jsonify({'error': 'Substitute request not found or already fulfilled'}), 404
    
    # Verify event is in the user's organization
    event = Event.query.filter_by(
        id=substitute_request.event_id,
        organization_id=organization.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user is trying to accept their own request
    if substitute_request.requested_by == user.id:
        return jsonify({'error': 'Cannot accept your own substitute request'}), 400
    
    # Update substitute request
    substitute_request.substitute_user_id = user.id
    substitute_request.status = 'fulfilled'
    substitute_request.fulfilled_at = datetime.utcnow()
    
    # Create or update RSVP for substitute
    substitute_rsvp = RSVP.query.filter_by(
        event_id=event.id,
        user_id=user.id
    ).first()
    
    if substitute_rsvp:
        substitute_rsvp.response = 'yes'
        substitute_rsvp.is_substitute = True
    else:
        substitute_rsvp = RSVP(
            event_id=event.id,
            user_id=user.id,
            response='yes',
            is_substitute=True,
            created_at=datetime.utcnow()
        )
        db.session.add(substitute_rsvp)
    
    # Update original user's RSVP
    original_rsvp = RSVP.query.filter_by(
        event_id=event.id,
        user_id=substitute_request.requested_by
    ).first()
    
    if original_rsvp:
        original_rsvp.response = 'no'
        original_rsvp.substitute_found = True
    
    db.session.commit()
    
    # Send notification to original user
    # TODO: Implement notification system
    
    return jsonify({
        'message': 'Substitute request accepted successfully',
        'event_name': event.name
    })

@substitutes_bp.route('/decline', methods=['POST'])
@jwt_required()
def decline_substitute_request():
    """Decline a substitute request"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    if not data.get('request_id'):
        return jsonify({'error': 'Request ID is required'}), 400
    
    # Find the substitute request
    substitute_request = SubstituteRequest.query.filter_by(
        id=data['request_id'],
        status='pending'
    ).first()
    
    if not substitute_request:
        return jsonify({'error': 'Substitute request not found or already fulfilled'}), 404
    
    # For now, just log the decline - in a full implementation,
    # we would track who declined and continue with the call list
    
    return jsonify({'message': 'Substitute request declined'})

@substitutes_bp.route('/call-list', methods=['GET'])
@jwt_required()
def get_call_list():
    """Get call list for substitute requests"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Get call list entries for this organization
    call_list = CallList.query.filter_by(
        organization_id=organization.id,
        is_active=True
    ).order_by(CallList.priority_order).all()
    
    result = []
    for entry in call_list:
        user_info = User.query.get(entry.user_id)
        if user_info:
            result.append({
                'id': entry.id,
                'user': {
                    'id': user_info.id,
                    'name': user_info.full_name,
                    'email': user_info.email
                },
                'priority_order': entry.priority_order,
                'available_for_substitution': entry.available_for_substitution,
                'last_substitute_date': entry.last_substitute_date.isoformat() if entry.last_substitute_date else None,
                'notes': entry.notes
            })
    
    return jsonify(result)

@substitutes_bp.route('/call-list', methods=['POST'])
@jwt_required()
def update_call_list():
    """Update call list (admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data.get('entries'):
        return jsonify({'error': 'Call list entries are required'}), 400
    
    # Clear existing entries
    CallList.query.filter_by(organization_id=organization.id).delete()
    
    # Add new entries
    for entry_data in data['entries']:
        entry = CallList(
            organization_id=organization.id,
            user_id=entry_data['user_id'],
            priority_order=entry_data['priority_order'],
            available_for_substitution=entry_data.get('available_for_substitution', True),
            notes=entry_data.get('notes', '')
        )
        db.session.add(entry)
    
    db.session.commit()
    
    return jsonify({'message': 'Call list updated successfully'})

@substitutes_bp.route('/availability', methods=['PUT'])
@jwt_required()
def update_substitute_availability():
    """Update user's availability for substitution"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    if 'available_for_substitution' not in data:
        return jsonify({'error': 'Availability status is required'}), 400
    
    # Find or create call list entry
    call_list_entry = CallList.query.filter_by(
        organization_id=organization.id,
        user_id=user.id
    ).first()
    
    if not call_list_entry:
        call_list_entry = CallList(
            organization_id=organization.id,
            user_id=user.id,
            priority_order=999,  # Default low priority
            available_for_substitution=data['available_for_substitution']
        )
        db.session.add(call_list_entry)
    else:
        call_list_entry.available_for_substitution = data['available_for_substitution']
    
    db.session.commit()
    
    return jsonify({'message': 'Substitute availability updated successfully'})

def _process_substitute_request(substitute_request):
    """Process substitute request by notifying potential substitutes"""
    # Get the event and organization
    event = Event.query.get(substitute_request.event_id)
    if not event:
        return
    
    organization = Organization.query.get(event.organization_id)
    if not organization:
        return
    
    # Get call list for this organization
    call_list = CallList.query.filter_by(
        organization_id=organization.id,
        is_default=True
    ).first()
    
    # If no default call list, get the first available one
    if not call_list:
        call_list = CallList.query.filter_by(
            organization_id=organization.id
        ).first()
    
    # Notify potential substitutes
    # TODO: Implement notification system to send emails/push notifications
    # For now, we'll just log
    print(f"Processing substitute request {substitute_request.id} for event {event.title}")
    if call_list:
        print(f"Using call list: {call_list.name}")
    else:
        print("No call list available for substitute requests")
    
    # In a full implementation, we would:
    # 1. Send notifications to users in priority order
    # 2. Wait for responses with timeout
    # 3. Move to next user if no response
    # 4. Track who was contacted and when
