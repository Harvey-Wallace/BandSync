from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import (db, User, Organization, Event, RSVP, Section, 
                   UserOrganization, EventCategory)
from datetime import datetime, timedelta
import csv
import io
import json
from werkzeug.security import generate_password_hash
import re
import uuid

bulk_ops_bp = Blueprint('bulk_ops', __name__)

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

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@bulk_ops_bp.route('/import-template', methods=['GET'])
@jwt_required()
def get_import_template():
    """Get CSV import template"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    template = {
        'headers': ['first_name', 'last_name', 'email', 'phone', 'section'],
        'sample_data': [
            ['John', 'Doe', 'john@example.com', '555-0123', 'Trumpet'],
            ['Jane', 'Smith', 'jane@example.com', '555-0456', 'Saxophone']
        ],
        'instructions': 'Fill in member data using the provided headers. Email is required.'
    }
    return jsonify(template)

@bulk_ops_bp.route('/export', methods=['GET'])
@jwt_required()
def export_organization_data():
    """Export organization data"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get members
    members = []
    for uo in organization.user_organizations:
        members.append({
            'id': uo.user.id,
            'name': uo.user.name,
            'email': uo.user.email,
            'role': uo.role,
            'section': uo.section.name if uo.section else None
        })
    
    # Get events
    events = []
    for event in organization.events:
        events.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.isoformat() if event.date else None,
            'location': event.location_address,
            'description': event.description
        })
    
    return jsonify({
        'organization': {
            'id': organization.id,
            'name': organization.name
        },
        'members': members,
        'events': events,
        'exported_at': datetime.utcnow().isoformat()
    })

@bulk_ops_bp.route('/import/members/preview', methods=['POST'])
@jwt_required()
def preview_member_import():
    """Preview member import from CSV"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400
    
    try:
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Expected columns
        required_columns = ['email', 'first_name', 'last_name']
        optional_columns = ['phone', 'section', 'role', 'instrument']
        
        # Validate headers
        headers = csv_reader.fieldnames
        missing_columns = [col for col in required_columns if col not in headers]
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'optional_columns': optional_columns
            }), 400
        
        # Process rows
        valid_rows = []
        invalid_rows = []
        existing_emails = set()
        
        # Get existing users in organization
        existing_users = {member.email for member in organization.members}
        
        row_num = 0
        for row in csv_reader:
            row_num += 1
            errors = []
            
            # Validate required fields
            if not row.get('email'):
                errors.append('Email is required')
            elif not validate_email(row['email']):
                errors.append('Invalid email format')
            elif row['email'] in existing_users:
                errors.append('User already exists in organization')
            elif row['email'] in existing_emails:
                errors.append('Duplicate email in import file')
            else:
                existing_emails.add(row['email'])
            
            if not row.get('first_name'):
                errors.append('First name is required')
            
            if not row.get('last_name'):
                errors.append('Last name is required')
            
            # Validate optional fields
            if row.get('role') and row['role'] not in ['Admin', 'Member']:
                errors.append('Role must be Admin or Member')
            
            row_data = {
                'row_number': row_num,
                'email': row.get('email', ''),
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'phone': row.get('phone', ''),
                'section': row.get('section', ''),
                'role': row.get('role', 'Member'),
                'instrument': row.get('instrument', ''),
                'errors': errors
            }
            
            if errors:
                invalid_rows.append(row_data)
            else:
                valid_rows.append(row_data)
        
        return jsonify({
            'total_rows': row_num,
            'valid_rows': len(valid_rows),
            'invalid_rows': len(invalid_rows),
            'valid_data': valid_rows[:10],  # Show first 10 for preview
            'invalid_data': invalid_rows,
            'headers': headers
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 400

@bulk_ops_bp.route('/import/members', methods=['POST'])
@jwt_required()
def import_members():
    """Import members from CSV"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data.get('members'):
        return jsonify({'error': 'Member data is required'}), 400
    
    created_users = []
    errors = []
    
    try:
        for member_data in data['members']:
            try:
                # Check if user already exists globally
                existing_user = User.query.filter_by(email=member_data['email']).first()
                
                if existing_user:
                    # Add to organization if not already a member
                    if existing_user not in organization.members:
                        membership = UserOrganization(
                            user_id=existing_user.id,
                            organization_id=organization.id,
                            role=member_data.get('role', 'Member')
                        )
                        db.session.add(membership)
                        created_users.append(existing_user.email)
                else:
                    # Create new user
                    new_user = User(
                        email=member_data['email'],
                        first_name=member_data['first_name'],
                        last_name=member_data['last_name'],
                        phone=member_data.get('phone', ''),
                        password_hash=generate_password_hash('TempPassword123!'),  # Temporary password
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(new_user)
                    db.session.flush()  # Get the user ID
                    
                    # Add to organization
                    membership = UserOrganization(
                        user_id=new_user.id,
                        organization_id=organization.id,
                        role=member_data.get('role', 'Member')
                    )
                    db.session.add(membership)
                    created_users.append(new_user.email)
                
            except Exception as e:
                errors.append(f"Error creating user {member_data['email']}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully imported {len(created_users)} members',
            'created_users': created_users,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

@bulk_ops_bp.route('/events/create', methods=['POST'])
@jwt_required()
def bulk_create_events():
    """Create multiple events at once"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data.get('events'):
        return jsonify({'error': 'Event data is required'}), 400
    
    created_events = []
    errors = []
    
    try:
        for event_data in data['events']:
            try:
                # Validate required fields
                if not event_data.get('name'):
                    errors.append('Event name is required')
                    continue
                
                if not event_data.get('start_datetime'):
                    errors.append(f'Start datetime is required for event: {event_data["name"]}')
                    continue
                
                # Parse datetime
                start_datetime = datetime.fromisoformat(event_data['start_datetime'])
                end_datetime = None
                if event_data.get('end_datetime'):
                    end_datetime = datetime.fromisoformat(event_data['end_datetime'])
                
                # Create event
                event = Event(
                    name=event_data['name'],
                    description=event_data.get('description', ''),
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location=event_data.get('location', ''),
                    organization_id=organization.id,
                    created_by=user.id,
                    created_at=datetime.utcnow(),
                    rsvp_required=event_data.get('rsvp_required', True),
                    rsvp_deadline=datetime.fromisoformat(event_data['rsvp_deadline']) if event_data.get('rsvp_deadline') else None,
                    max_attendees=event_data.get('max_attendees'),
                    is_recurring=event_data.get('is_recurring', False)
                )
                
                db.session.add(event)
                db.session.flush()
                
                created_events.append({
                    'id': event.id,
                    'name': event.name,
                    'start_datetime': event.start_datetime.isoformat()
                })
                
            except Exception as e:
                errors.append(f"Error creating event {event_data.get('name', 'Unknown')}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully created {len(created_events)} events',
            'created_events': created_events,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Bulk event creation failed: {str(e)}'}), 500

@bulk_ops_bp.route('/events/recurring', methods=['POST'])
@jwt_required()
def create_recurring_events():
    """Create recurring events"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'start_datetime', 'recurrence_type', 'recurrence_count']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        base_start = datetime.fromisoformat(data['start_datetime'])
        base_end = None
        if data.get('end_datetime'):
            base_end = datetime.fromisoformat(data['end_datetime'])
        
        recurrence_type = data['recurrence_type']  # 'daily', 'weekly', 'monthly'
        recurrence_count = data['recurrence_count']
        
        created_events = []
        
        for i in range(recurrence_count):
            # Calculate datetime for this occurrence
            if recurrence_type == 'daily':
                start_datetime = base_start + timedelta(days=i)
                end_datetime = base_end + timedelta(days=i) if base_end else None
            elif recurrence_type == 'weekly':
                start_datetime = base_start + timedelta(weeks=i)
                end_datetime = base_end + timedelta(weeks=i) if base_end else None
            elif recurrence_type == 'monthly':
                # Simple monthly recurrence (same day of month)
                months_ahead = i
                year = base_start.year + (base_start.month + months_ahead - 1) // 12
                month = (base_start.month + months_ahead - 1) % 12 + 1
                start_datetime = base_start.replace(year=year, month=month)
                if base_end:
                    end_datetime = base_end.replace(year=year, month=month)
                else:
                    end_datetime = None
            else:
                return jsonify({'error': 'Invalid recurrence type'}), 400
            
            # Create event
            event_name = f"{data['name']}"
            if recurrence_count > 1:
                event_name += f" ({i + 1})"
            
            event = Event(
                name=event_name,
                description=data.get('description', ''),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=data.get('location', ''),
                organization_id=organization.id,
                created_by=user.id,
                created_at=datetime.utcnow(),
                rsvp_required=data.get('rsvp_required', True),
                rsvp_deadline=start_datetime - timedelta(days=1),  # Default deadline
                is_recurring=True
            )
            
            db.session.add(event)
            db.session.flush()
            
            created_events.append({
                'id': event.id,
                'name': event.name,
                'start_datetime': event.start_datetime.isoformat()
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully created {len(created_events)} recurring events',
            'created_events': created_events
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Recurring event creation failed: {str(e)}'}), 500

@bulk_ops_bp.route('/export/members', methods=['GET'])
@jwt_required()
def export_members():
    """Export organization members to CSV"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get all members
    members = organization.members
    
    # Create CSV data
    csv_data = []
    for member in members:
        membership = UserOrganization.query.filter_by(
            user_id=member.id,
            organization_id=organization.id
        ).first()
        
        csv_data.append({
            'email': member.email,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'phone': member.phone or '',
            'role': membership.role if membership else 'Member',
            'joined_date': membership.joined_at.isoformat() if membership and membership.joined_at else '',
            'last_login': member.last_login.isoformat() if member.last_login else '',
            'is_active': member.is_active
        })
    
    return jsonify({
        'filename': f'{organization.name}_members_{datetime.now().strftime("%Y%m%d")}.csv',
        'data': csv_data
    })

@bulk_ops_bp.route('/export/events', methods=['GET'])
@jwt_required()
def export_events():
    """Export organization events to CSV"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Event.query.filter_by(organization_id=organization.id)
    
    if start_date:
        query = query.filter(Event.start_datetime >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Event.start_datetime <= datetime.fromisoformat(end_date))
    
    events = query.order_by(Event.start_datetime).all()
    
    # Create CSV data
    csv_data = []
    for event in events:
        rsvp_count = RSVP.query.filter_by(event_id=event.id).count()
        yes_count = RSVP.query.filter_by(event_id=event.id, response='yes').count()
        
        csv_data.append({
            'name': event.name,
            'description': event.description or '',
            'start_datetime': event.start_datetime.isoformat(),
            'end_datetime': event.end_datetime.isoformat() if event.end_datetime else '',
            'location': event.location or '',
            'rsvp_required': event.rsvp_required,
            'rsvp_deadline': event.rsvp_deadline.isoformat() if event.rsvp_deadline else '',
            'max_attendees': event.max_attendees or '',
            'rsvp_count': rsvp_count,
            'yes_count': yes_count,
            'created_at': event.created_at.isoformat()
        })
    
    return jsonify({
        'filename': f'{organization.name}_events_{datetime.now().strftime("%Y%m%d")}.csv',
        'data': csv_data
    })

@bulk_ops_bp.route('/delete/events', methods=['POST'])
@jwt_required()
def bulk_delete_events():
    """Delete multiple events"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data.get('event_ids'):
        return jsonify({'error': 'Event IDs are required'}), 400
    
    try:
        # Verify all events belong to the organization
        events = Event.query.filter(
            Event.id.in_(data['event_ids']),
            Event.organization_id == organization.id
        ).all()
        
        if len(events) != len(data['event_ids']):
            return jsonify({'error': 'Some events not found or not accessible'}), 404
        
        # Delete RSVPs first
        for event in events:
            RSVP.query.filter_by(event_id=event.id).delete()
        
        # Delete events
        for event in events:
            db.session.delete(event)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {len(events)} events'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Bulk delete failed: {str(e)}'}), 500
