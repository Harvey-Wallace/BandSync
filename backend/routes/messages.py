from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Organization, MessageThread, Message, Section
from datetime import datetime
import uuid
from sqlalchemy import or_, and_

messages_bp = Blueprint('messages', __name__)

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

@messages_bp.route('/threads', methods=['GET'])
@jwt_required()
def get_message_threads():
    """Get all message threads for the current user"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Get threads where user is in the same organization
    threads = MessageThread.query.filter(
        MessageThread.organization_id == organization.id
    ).order_by(MessageThread.last_message_at.desc()).all()
    
    result = []
    for thread in threads:
        # Get last message
        last_message = Message.query.filter_by(
            thread_id=thread.id
        ).order_by(Message.sent_at.desc()).first()
        
        # Get participant info - Use message recipients instead
        participants = []
        
        thread_data = {
            'id': thread.id,
            'subject': thread.subject,
            'thread_type': thread.thread_type,
            'created_by': thread.created_by,
            'created_at': thread.created_at.isoformat(),
            'last_message_at': thread.last_message_at.isoformat() if thread.last_message_at else None,
            'last_message': {
                'content': last_message.content[:100] + '...' if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
                'sender_name': last_message.sender.name if last_message else None,
                'sent_at': last_message.sent_at.isoformat() if last_message else None
            } if last_message else None,
            'participants': [],  # Empty for now since we don't have participant tracking
            'participant_count': 0,
            'unread_count': 0  # Simplified for now
        }
        result.append(thread_data)
    
    return jsonify(result)

@messages_bp.route('/threads/<int:thread_id>/messages', methods=['GET'])
@jwt_required()
def get_thread_messages(thread_id):
    """Get all messages in a specific thread"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Verify user has access to this thread
    thread = MessageThread.query.filter_by(
        id=thread_id,
        organization_id=organization.id
    ).first()
    
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    participant_ids = thread.participant_ids.split(',') if thread.participant_ids else []
    if str(user.id) not in participant_ids and thread.created_by != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get messages with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = Message.query.filter_by(
        thread_id=thread_id
    ).order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        thread_id=thread_id,
        is_read=False
    ).filter(Message.sender_id != user.id).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    result = {
        'messages': [{
            'id': msg.id,
            'content': msg.content,
            'sender': {
                'id': msg.sender.id,
                'name': msg.sender.full_name
            },
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        } for msg in reversed(messages.items)],
        'pagination': {
            'current_page': messages.page,
            'per_page': messages.per_page,
            'total': messages.total,
            'pages': messages.pages,
            'has_prev': messages.has_prev,
            'has_next': messages.has_next
        }
    }
    
    return jsonify(result)

@messages_bp.route('/threads', methods=['POST'])
@jwt_required()
def create_message_thread():
    """Create a new message thread"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    # Validate input
    if not data.get('subject'):
        return jsonify({'error': 'Subject is required'}), 400
    
    if not data.get('participants'):
        return jsonify({'error': 'At least one participant is required'}), 400
    
    # Validate participants are in the organization
    participant_ids = data['participants']
    participants = User.query.filter(
        User.id.in_(participant_ids),
        User.organizations.any(Organization.id == organization.id)
    ).all()
    
    if len(participants) != len(participant_ids):
        return jsonify({'error': 'Some participants are not in the organization'}), 400
    
    # Create thread
    thread = MessageThread(
        id=str(uuid.uuid4()),
        subject=data['subject'],
        thread_type=data.get('thread_type', 'direct'),
        organization_id=organization.id,
        created_by=user.id,
        participant_ids=','.join(map(str, participant_ids)),
        created_at=datetime.utcnow()
    )
    
    db.session.add(thread)
    
    # Add initial message if provided
    if data.get('initial_message'):
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            sender_id=user.id,
            content=data['initial_message'],
            created_at=datetime.utcnow()
        )
        db.session.add(message)
        thread.last_message_at = message.created_at
    
    db.session.commit()
    
    return jsonify({
        'thread_id': thread.id,
        'message': 'Thread created successfully'
    }), 201

@messages_bp.route('/threads/<int:thread_id>/messages', methods=['POST'])
@jwt_required()
def send_message(thread_id):
    """Send a message to a thread"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Message content is required'}), 400
    
    # Verify user has access to this thread
    thread = MessageThread.query.filter_by(
        id=thread_id,
        organization_id=organization.id
    ).first()
    
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    participant_ids = thread.participant_ids.split(',') if thread.participant_ids else []
    if str(user.id) not in participant_ids and thread.created_by != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Create message
    message = Message(
        id=str(uuid.uuid4()),
        thread_id=thread_id,
        sender_id=user.id,
        content=data['content'],
        created_at=datetime.utcnow()
    )
    
    db.session.add(message)
    
    # Update thread last message time
    thread.last_message_at = message.created_at
    db.session.commit()
    
    return jsonify({
        'message_id': message.id,
        'message': 'Message sent successfully'
    }), 201

@messages_bp.route('/compose', methods=['GET'])
@jwt_required()
def get_compose_options():
    """Get options for composing messages (users, sections, etc.)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Get all users in the organization
    users = User.query.filter(
        User.organizations.any(Organization.id == organization.id)
    ).all()
    
    # Get all sections in the organization
    sections = Section.query.filter_by(organization_id=organization.id).all()
    
    result = {
        'users': [{'id': u.id, 'name': u.full_name, 'email': u.email} for u in users],
        'sections': [{'id': s.id, 'name': s.name, 'description': s.description} for s in sections]
    }
    
    return jsonify(result)

@messages_bp.route('/threads/<int:thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    """Delete a message thread (admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    thread = MessageThread.query.filter_by(
        id=thread_id,
        organization_id=organization.id
    ).first()
    
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    # Delete all messages in the thread
    Message.query.filter_by(thread_id=thread_id).delete()
    
    # Delete the thread
    db.session.delete(thread)
    db.session.commit()
    
    return jsonify({'message': 'Thread deleted successfully'})

@messages_bp.route('/broadcast', methods=['POST'])
@jwt_required()
def broadcast_message():
    """Send a broadcast message to multiple users or sections (admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data.get('subject') or not data.get('content'):
        return jsonify({'error': 'Subject and content are required'}), 400
    
    if not data.get('recipients'):
        return jsonify({'error': 'Recipients are required'}), 400
    
    # Determine recipients
    recipient_ids = set()
    
    # Add direct user IDs
    if 'user_ids' in data['recipients']:
        recipient_ids.update(data['recipients']['user_ids'])
    
    # Add users from sections
    if 'section_ids' in data['recipients']:
        for section_id in data['recipients']['section_ids']:
            section = Section.query.get(section_id)
            if section and section.organization_id == organization.id:
                # Get all users in this section
                section_users = User.query.filter(
                    User.organizations.any(Organization.id == organization.id)
                ).all()
                # Note: This would need proper section membership table
                # For now, we'll skip section-based targeting
                pass
    
    # Send to all organization members if specified
    if data['recipients'].get('all_members'):
        all_users = User.query.filter(
            User.organizations.any(Organization.id == organization.id)
        ).all()
        recipient_ids.update([u.id for u in all_users])
    
    # Create individual threads for each recipient
    threads_created = 0
    for recipient_id in recipient_ids:
        if recipient_id == user.id:  # Don't send to self
            continue
            
        # Create thread
        thread = MessageThread(
            id=str(uuid.uuid4()),
            subject=data['subject'],
            thread_type='broadcast',
            organization_id=organization.id,
            created_by=user.id,
            participant_ids=str(recipient_id),
            created_at=datetime.utcnow()
        )
        
        db.session.add(thread)
        
        # Add message
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            sender_id=user.id,
            content=data['content'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        thread.last_message_at = message.created_at
        threads_created += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Broadcast message sent to {threads_created} recipients',
        'recipients_count': threads_created
    }), 201

@messages_bp.route('/', methods=['GET'])
@jwt_required()
def get_messages():
    """Get messages (redirects to threads for compatibility)"""
    return get_message_threads()

@messages_bp.route('/send', methods=['POST'])
@jwt_required()
def send_simple_message():
    """Send a new message (creates a new thread)"""
    data = request.get_json()
    user, organization = get_current_user_and_org()
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Extract data
    subject = data.get('subject', 'New Message')
    content = data.get('content', '')
    recipient_type = data.get('recipient_type', 'organization')
    
    # Create new thread (note: no participant tracking needed since all org members can see all threads)
    thread = MessageThread(
        organization_id=organization.id,
        subject=subject,
        created_by=user.id,
        last_message_at=datetime.utcnow()
    )
    
    db.session.add(thread)
    db.session.flush()
    
    # Create the message
    message = Message(
        thread_id=thread.id,
        sender_id=user.id,
        content=content,
        sent_at=datetime.utcnow()
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'message': 'Message sent successfully',
        'thread_id': thread.id,
        'message_id': message.id
    }), 201
