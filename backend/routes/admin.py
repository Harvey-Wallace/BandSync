from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, db, Organization, Section, EmailLog, UserOrganization, Event, RSVP
from datetime import datetime
import cloudinary
import cloudinary.uploader
import os
from werkzeug.utils import secure_filename
from services.calendar_service import calendar_service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    users = User.query.filter_by(organization_id=org_id).all()
    return jsonify([{
        'id': u.id, 
        'username': u.username, 
        'email': u.email, 
        'name': u.name,
        'role': u.role,
        'section_id': u.section_id,
        'section_name': u.section.name if u.section else None
    } for u in users])

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    u = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    data = request.get_json()
    
    # Update user fields
    u.role = data.get('role', u.role)
    u.name = data.get('name', u.name)
    u.email = data.get('email', u.email)
    u.phone = data.get('phone', u.phone)
    u.address = data.get('address', u.address)
    u.avatar_url = data.get('avatar_url', u.avatar_url)
    
    # Handle section assignment
    if 'section_id' in data:
        section_id = data.get('section_id')
        if section_id:
            # Verify section belongs to same organization
            section = Section.query.filter_by(id=section_id, organization_id=org_id).first()
            if not section:
                return jsonify({'msg': 'Section not found'}), 404
            u.section_id = section_id
        else:
            u.section_id = None
    
    # Only update username if provided and it's different
    new_username = data.get('username')
    if new_username and new_username != u.username:
        # Check if username is already taken
        existing_user = User.query.filter_by(username=new_username, organization_id=org_id).first()
        if existing_user:
            return jsonify({'msg': 'Username already exists'}), 400
        u.username = new_username
    
    # Only update email if provided and it's different
    new_email = data.get('email')
    if new_email and new_email != u.email:
        # Check if email is already taken
        existing_user = User.query.filter_by(email=new_email, organization_id=org_id).first()
        if existing_user:
            return jsonify({'msg': 'Email already exists'}), 400
        u.email = new_email
    
    db.session.commit()
    return jsonify({
        'msg': 'User updated',
        'user': {
            'id': u.id,
            'username': u.username,
            'name': u.name,
            'email': u.email,
            'phone': u.phone,
            'address': u.address,
            'role': u.role,
            'avatar_url': u.avatar_url,
            'section_id': u.section_id,
            'section_name': u.section.name if u.section else None
        }
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    u = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    db.session.delete(u)
    db.session.commit()
    return jsonify({'msg': 'User deleted'})


# Get or update organization info (name, etc.)
@admin_bp.route('/organization', methods=['GET', 'PUT'])
@jwt_required()
def organization():
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    org = Organization.query.get_or_404(org_id)
    if request.method == 'GET':
        return jsonify({
            'id': org.id, 
            'name': org.name,
            'logo_url': org.logo_url,
            'theme_color': org.theme_color
        })
    if request.method == 'PUT':
        data = request.get_json()
        if 'name' in data and data['name']:
            org.name = data['name']
        if 'logo_url' in data:
            org.logo_url = data['logo_url']
        if 'theme_color' in data and data['theme_color']:
            org.theme_color = data['theme_color']
        
        db.session.commit()
        return jsonify({
            'msg': 'Organization updated',
            'name': org.name,
            'logo_url': org.logo_url,
            'theme_color': org.theme_color
        })

@admin_bp.route('/upload-logo', methods=['POST'])
@jwt_required()
def upload_logo():
    """Upload organization logo to Cloudinary"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed'}), 400
    
    # Validate file size (max 5MB)
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > 5 * 1024 * 1024:  # 5MB limit
        return jsonify({'error': 'File size too large. Maximum size is 5MB'}), 400
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        org_id = claims.get('organization_id')
        
        # Upload to Cloudinary with organization-specific folder
        result = cloudinary.uploader.upload(
            file,
            folder=f"bandsync/org_{org_id}/logos",
            transformation=[
                {'width': 400, 'height': 200, 'crop': 'limit'},
                {'quality': 'auto'},
                {'format': 'auto'}
            ],
            public_id=f"logo_{org_id}",
            overwrite=True
        )
        
        logo_url = result['secure_url']
        
        # Update organization with new logo URL
        org = Organization.query.get_or_404(org_id)
        org.logo_url = logo_url
        db.session.commit()
        
        return jsonify({
            'logo_url': logo_url,
            'msg': 'Logo uploaded successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user in the organization"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    data = request.get_json()
    org_id = claims.get('organization_id')
    
    # Validate required fields
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            role=data.get('role', 'Member'),
            organization_id=org_id
        )
        
        # Set password (either provided or generate temporary)
        password = data.get('password', f"temp_{data['username']}123")
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send invitation email if requested
        if data.get('send_invitation', False):
            try:
                email_sent = send_invitation_email(new_user, password)
                if not email_sent:
                    print(f"Warning: Failed to send invitation email to {new_user.email}")
            except Exception as e:
                print(f"Error sending invitation email: {str(e)}")
                # Don't fail the user creation if email fails
        
        return jsonify({
            'msg': 'User created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'name': new_user.name,
                'role': new_user.role
            },
            'temporary_password': password if not data.get('password') else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/invite', methods=['POST'])
@jwt_required()
def send_user_invitation(user_id):
    """Send invitation email to an existing user"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    user = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    
    try:
        # Generate a temporary password
        temp_password = f"temp_{user.username}123"
        user.set_password(temp_password)
        db.session.commit()
        
        # Send invitation email
        try:
            email_sent = send_invitation_email(user, temp_password)
            if not email_sent:
                return jsonify({'error': 'Failed to send invitation email'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to send invitation email: {str(e)}'}), 500
        
        return jsonify({
            'msg': 'Invitation sent successfully',
            'temporary_password': temp_password
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to send invitation: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    u = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    return jsonify({
        'id': u.id,
        'username': u.username,
        'name': u.name,
        'email': u.email,
        'phone': u.phone,
        'address': u.address,
        'role': u.role,
        'avatar_url': u.avatar_url,
        'section_id': u.section_id,
        'section_name': u.section.name if u.section else None
    })

# Section Management Endpoints
@admin_bp.route('/sections', methods=['GET'])
@jwt_required()
def get_sections():
    """Get all sections for the organization"""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    sections = Section.query.filter_by(organization_id=org_id).order_by(Section.display_order).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'display_order': s.display_order,
        'member_count': len(s.users)
    } for s in sections])

@admin_bp.route('/sections', methods=['POST'])
@jwt_required()
def create_section():
    """Create a new section (Admin only)"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    data = request.get_json()
    
    # Check if section name already exists
    existing = Section.query.filter_by(name=data['name'], organization_id=org_id).first()
    if existing:
        return jsonify({'error': 'Section name already exists'}), 400
    
    # Get next display order
    max_order = db.session.query(db.func.max(Section.display_order)).filter_by(organization_id=org_id).scalar() or 0
    
    section = Section(
        name=data['name'],
        description=data.get('description', ''),
        organization_id=org_id,
        display_order=max_order + 1
    )
    
    db.session.add(section)
    db.session.commit()
    
    return jsonify({
        'msg': 'Section created',
        'section': {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'display_order': section.display_order,
            'member_count': 0
        }
    })

@admin_bp.route('/sections/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_section(section_id):
    """Update a section (Admin only)"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    section = Section.query.filter_by(id=section_id, organization_id=org_id).first_or_404()
    
    data = request.get_json()
    
    # Check if new name conflicts with existing section
    if 'name' in data and data['name'] != section.name:
        existing = Section.query.filter_by(name=data['name'], organization_id=org_id).first()
        if existing:
            return jsonify({'error': 'Section name already exists'}), 400
        section.name = data['name']
    
    if 'description' in data:
        section.description = data['description']
    
    if 'display_order' in data:
        section.display_order = data['display_order']
    
    db.session.commit()
    
    return jsonify({
        'msg': 'Section updated',
        'section': {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'display_order': section.display_order,
            'member_count': len(section.users)
        }
    })

@admin_bp.route('/sections/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    """Delete a section (Admin only)"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    section = Section.query.filter_by(id=section_id, organization_id=org_id).first_or_404()
    
    # Check if section has members
    if section.users:
        return jsonify({'error': 'Cannot delete section with members. Please reassign members first.'}), 400
    
    db.session.delete(section)
    db.session.commit()
    
    return jsonify({'msg': 'Section deleted'})

@admin_bp.route('/users/<int:user_id>/section', methods=['PUT'])
@jwt_required()
def assign_user_section(user_id):
    """Assign a user to a section (Admin only)"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    user = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    
    data = request.get_json()
    section_id = data.get('section_id')
    
    if section_id:
        # Verify section belongs to same organization
        section = Section.query.filter_by(id=section_id, organization_id=org_id).first()
        if not section:
            return jsonify({'error': 'Section not found'}), 404
        user.section_id = section_id
    else:
        # Remove section assignment
        user.section_id = None
    
    db.session.commit()
    
    return jsonify({
        'msg': 'User section updated',
        'user': {
            'id': user.id,
            'username': user.username,
            'section_id': user.section_id,
            'section_name': user.section.name if user.section else None
        }
    })

@admin_bp.route('/email-logs', methods=['GET'])
@jwt_required()
def get_email_logs():
    """Get email logs for current organization"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    email_type = request.args.get('email_type')
    status = request.args.get('status')
    
    # Build query
    query = EmailLog.query.filter_by(organization_id=org_id)
    
    if email_type:
        query = query.filter_by(email_type=email_type)
    if status:
        query = query.filter_by(status=status)
    
    # Get paginated results
    logs = query.order_by(EmailLog.sent_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'email_type': log.email_type,
            'user_email': log.user.email if log.user else None,
            'user_name': log.user.name if log.user else None,
            'event_title': log.event.title if log.event else None,
            'sent_at': log.sent_at.isoformat(),
            'status': log.status,
            'error_message': log.error_message,
            'sendgrid_message_id': log.sendgrid_message_id
        } for log in logs.items],
        'pagination': {
            'page': logs.page,
            'pages': logs.pages,
            'per_page': logs.per_page,
            'total': logs.total
        }
    })

@admin_bp.route('/email-stats', methods=['GET'])
@jwt_required()
def get_email_stats():
    """Get email statistics for current organization"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    
    # Get statistics
    total_emails = EmailLog.query.filter_by(organization_id=org_id).count()
    sent_emails = EmailLog.query.filter_by(organization_id=org_id, status='sent').count()
    failed_emails = EmailLog.query.filter_by(organization_id=org_id, status='failed').count()
    
    # Get email types breakdown
    email_types = db.session.query(EmailLog.email_type, db.func.count()).filter_by(
        organization_id=org_id
    ).group_by(EmailLog.email_type).all()
    
    return jsonify({
        'total_emails': total_emails,
        'sent_emails': sent_emails,
        'failed_emails': failed_emails,
        'success_rate': (sent_emails / total_emails * 100) if total_emails > 0 else 0,
        'email_types': [{'type': t[0], 'count': t[1]} for t in email_types]
    })

@admin_bp.route('/scheduled-jobs', methods=['GET'])
@jwt_required()
def get_scheduled_jobs():
    """Get status of scheduled email jobs"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    try:
        from services.scheduled_tasks import task_service
        jobs = task_service.get_scheduled_jobs()
        return jsonify({'jobs': jobs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/send-test-notification', methods=['POST'])
@jwt_required()
def send_test_notification():
    """Send a test notification to admin"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    user_id = get_jwt_identity()
    org_id = claims.get('organization_id')
    
    try:
        from services.email_service import EmailService
        email_service = EmailService()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Send test email
        success = email_service._send_email(
            to_emails=[user.email],
            subject="BandSync Admin Test",
            html_content=f"""
            <h2>Admin Test Email</h2>
            <p>Hello {user.name or user.username},</p>
            <p>This is a test email sent from the BandSync admin panel.</p>
            <p>Organization: {org_id}</p>
            <p>Time: {datetime.utcnow().isoformat()}</p>
            <br>
            <p>Best regards,<br>BandSync System</p>
            """,
            text_content=f"Admin test email for {user.name or user.username}"
        )
        
        if success:
            return jsonify({'message': 'Test email sent successfully'})
        else:
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to send test email: {str(e)}'}), 500

@admin_bp.route('/calendar-stats', methods=['GET'])
@jwt_required()
def get_calendar_stats():
    """Get calendar usage statistics for current organization"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    
    try:
        # Get calendar info
        calendar_info = calendar_service.get_calendar_subscription_info(org_id)
        
        # Get event count
        from models import Event
        total_events = Event.query.filter_by(organization_id=org_id, is_template=False).count()
        upcoming_events = Event.query.filter_by(organization_id=org_id, is_template=False).filter(
            Event.date >= datetime.utcnow()
        ).count()
        
        # Get organization info
        organization = Organization.query.get(org_id)
        
        return jsonify({
            'organization_name': organization.name,
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'calendar_feeds': {
                'organization': calendar_info.get('organization', {}).get('url'),
                'public': calendar_info.get('public', {}).get('url'),
                'sections': len(calendar_info.get('sections', []))
            },
            'calendar_info': calendar_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-calendar-feed', methods=['POST'])
@jwt_required()
def test_calendar_feed():
    """Test calendar feed generation"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    
    try:
        # Generate test calendar
        ical_data = calendar_service.generate_organization_calendar(org_id)
        
        # Count events
        event_count = ical_data.count(b'BEGIN:VEVENT')
        
        return jsonify({
            'success': True,
            'message': f'Calendar feed generated successfully',
            'event_count': event_count,
            'feed_size_bytes': len(ical_data),
            'feed_url': calendar_service.get_calendar_url('org', org_id)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate calendar feed: {str(e)}'}), 500

def send_invitation_email(user, password):
    """Send invitation email to user using the proper email service"""
    try:
        from services.email_service import email_service
        
        # Get the current admin user who is sending the invitation
        current_user_id = get_jwt_identity()
        inviting_admin = User.query.get(current_user_id)
        
        if not inviting_admin:
            print(f"Warning: Could not find admin user with ID {current_user_id}")
            return False
        
        # Send the invitation email using the proper email service
        success = email_service.send_user_invitation(user, password, inviting_admin)
        
        if success:
            print(f"Invitation email sent successfully to {user.email}")
        else:
            print(f"Failed to send invitation email to {user.email}")
            
        return success
        
    except Exception as e:
        print(f"Error sending invitation email: {str(e)}")
        return False

# Public endpoint to get all users with section info (for dashboard RSVP display)
@admin_bp.route('/users/all', methods=['GET'])
@jwt_required()
def get_all_users():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    users = User.query.filter_by(organization_id=org_id).all()
    users_data = []
    
    for u in users:
        user_data = {
            'id': u.id,
            'username': u.username,
            'name': u.name or u.username,
            'display_name': u.name or u.username,
            'section_id': u.section_id,
            'section_name': u.section.name if u.section else None
        }
        users_data.append(user_data)
    
    return jsonify(users_data)

@admin_bp.route('/users/<int:user_id>/avatar/upload', methods=['POST'])
@jwt_required()
def upload_user_avatar(user_id):
    """Upload user avatar to Cloudinary"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed'}), 400
    
    # Validate file size (max 5MB)
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > 5 * 1024 * 1024:  # 5MB limit
        return jsonify({'error': 'File size too large. Maximum size is 5MB'}), 400
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        org_id = claims.get('organization_id')
        
        # Verify user exists and belongs to the same organization
        user = User.query.filter_by(id=user_id, organization_id=org_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Upload to Cloudinary with user-specific folder
        result = cloudinary.uploader.upload(
            file,
            folder=f"bandsync/org_{org_id}/avatars",
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face'},
                {'quality': 'auto'},
                {'format': 'auto'}
            ],
            public_id=f"user_{user_id}",
            overwrite=True
        )
        
        avatar_url = result['secure_url']
        
        # Update user with new avatar URL
        user.avatar_url = avatar_url
        db.session.commit()
        
        return jsonify({
            'avatar_url': avatar_url,
            'msg': 'Avatar uploaded successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
