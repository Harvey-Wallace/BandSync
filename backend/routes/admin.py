from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import (
    User, db, Organization, Section, EmailLog, UserOrganization, Event, RSVP,
    EventFieldResponse, EventAttachment, EventSurvey, SurveyResponse, 
    MessageThread, Message, MessageRecipient, SubstituteRequest, CallList, CallListMember
)
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
    
    # Get users through UserOrganization relationship for multi-organization support
    user_orgs = UserOrganization.query.filter_by(
        organization_id=org_id,
        is_active=True
    ).all()
    
    users_data = []
    for user_org in user_orgs:
        user = user_org.user
        users_data.append({
            'id': user.id, 
            'username': user.username, 
            'email': user.email, 
            'name': user.name,
            'role': user_org.role,  # Use role from UserOrganization
            'section_id': user_org.section_id,
            'section_name': user_org.section.name if user_org.section else None
        })
    
    return jsonify(users_data)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    
    # Find user through UserOrganization relationship
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id,
        is_active=True
    ).first_or_404()
    
    u = user_org.user
    data = request.get_json()
    
    # Update user fields
    u.name = data.get('name', u.name)
    u.email = data.get('email', u.email)
    u.phone = data.get('phone', u.phone)
    u.address = data.get('address', u.address)
    u.avatar_url = data.get('avatar_url', u.avatar_url)
    
    # Update role in UserOrganization (not in User table)
    user_org.role = data.get('role', user_org.role)
    
    # Handle section assignment in UserOrganization
    if 'section_id' in data:
        section_id = data.get('section_id')
        if section_id:
            # Verify section belongs to same organization
            section = Section.query.filter_by(id=section_id, organization_id=org_id).first()
            if not section:
                return jsonify({'msg': 'Section not found'}), 404
            user_org.section_id = section_id
        else:
            user_org.section_id = None
    
    # Only update username if provided and it's different
    new_username = data.get('username')
    if new_username and new_username != u.username:
        # Check if username is already taken globally (not just in org)
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            return jsonify({'msg': 'Username already exists'}), 400
        u.username = new_username
    
    # Only update email if provided and it's different
    new_email = data.get('email')
    if new_email and new_email != u.email:
        # Check if email is already taken globally (not just in org)
        existing_user = User.query.filter_by(email=new_email).first()
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
    
    # Find user through UserOrganization relationship
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id,
        is_active=True
    ).first_or_404()
    
    user = user_org.user
    
    try:
        print(f"Starting removal process for user {user_id} from organization {org_id}")
        
        # Check if user belongs to other organizations
        other_org_count = UserOrganization.query.filter(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id != org_id,
            UserOrganization.is_active == True
        ).count()
        
        if other_org_count > 0:
            # User belongs to other organizations, just remove from current org
            print(f"User belongs to {other_org_count} other organizations. Removing from current org only.")
            
            # Delete organization-specific RSVPs (events from this org)
            try:
                rsvp_count = db.session.execute(
                    db.text("""
                        DELETE FROM rsvp 
                        WHERE user_id = :user_id 
                        AND event_id IN (
                            SELECT id FROM event WHERE organization_id = :org_id
                        )
                    """), 
                    {"user_id": user_id, "org_id": org_id}
                ).rowcount
                print(f"Deleted {rsvp_count} RSVPs for this organization")
            except Exception as e:
                print(f"Error deleting RSVPs: {e}")
                db.session.execute(db.text("DELETE FROM rsvp WHERE user_id = :user_id AND event_id IN (SELECT id FROM event WHERE organization_id = :org_id)"), {"user_id": user_id, "org_id": org_id})
            
            # Remove user from this organization
            db.session.delete(user_org)
            
            # Update user's current organization if this was their current org
            if user.current_organization_id == org_id:
                # Set to their first remaining organization
                remaining_org = UserOrganization.query.filter_by(
                    user_id=user_id,
                    is_active=True
                ).first()
                if remaining_org:
                    user.current_organization_id = remaining_org.organization_id
                else:
                    user.current_organization_id = None
            
            db.session.commit()
            print(f"Successfully removed user {user_id} from organization {org_id}")
            return jsonify({'msg': 'User removed from organization successfully'})
        
        else:
            # User only belongs to this organization, do full deletion
            print(f"User only belongs to this organization. Performing full deletion.")
            
            # Delete all records that reference this user (original full deletion logic)
            # 1. Delete RSVPs
            try:
                rsvp_count = RSVP.query.filter_by(user_id=user_id).delete()
                print(f"Deleted {rsvp_count} RSVPs")
            except Exception as e:
                # Handle potential column name mismatch (timestamp vs created_at)
                if "timestamp does not exist" in str(e):
                    print(f"RSVP table schema mismatch detected, trying alternative deletion method")
                    # Use raw SQL to delete RSVPs if model is out of sync
                    db.session.execute(db.text("DELETE FROM rsvp WHERE user_id = :user_id"), {"user_id": user_id})
                    print("Deleted RSVPs using raw SQL")
                else:
                    print(f"Error deleting RSVPs: {e}")
                    raise
        
        # 2. Delete email logs
        email_log_count = EmailLog.query.filter_by(user_id=user_id).delete()
        print(f"Deleted {email_log_count} email logs")
        
        # 3. Delete user organization relationships
        user_org_count = UserOrganization.query.filter_by(user_id=user_id).delete()
        print(f"Deleted {user_org_count} user organization relationships")
        
        # 4. Delete event field responses
        try:
            field_response_count = EventFieldResponse.query.filter_by(user_id=user_id).delete()
            print(f"Deleted {field_response_count} event field responses")
        except Exception as e:
            print(f"Error deleting event field responses: {e}")
        
        # 5. Delete survey responses
        try:
            survey_response_count = SurveyResponse.query.filter_by(user_id=user_id).delete()
            print(f"Deleted {survey_response_count} survey responses")
        except Exception as e:
            print(f"Error deleting survey responses: {e}")
        
        # 6. Delete message recipients
        try:
            message_recipient_count = MessageRecipient.query.filter_by(user_id=user_id).delete()
            print(f"Deleted {message_recipient_count} message recipients")
        except Exception as e:
            print(f"Error deleting message recipients: {e}")
        
        # 7. Delete substitute requests (both requested_by and filled_by)
        try:
            substitute_request_count = SubstituteRequest.query.filter_by(requested_by=user_id).delete()
            substitute_filled_count = SubstituteRequest.query.filter_by(filled_by=user_id).update({'filled_by': None})
            print(f"Deleted {substitute_request_count} substitute requests, updated {substitute_filled_count} filled requests")
        except Exception as e:
            print(f"Error handling substitute requests: {e}")
        
        # 8. Delete call list entries
        try:
            call_list_count = CallList.query.filter_by(user_id=user_id).delete()
            call_list_member_count = CallListMember.query.filter_by(user_id=user_id).delete()
            print(f"Deleted {call_list_count} call list entries and {call_list_member_count} call list members")
        except Exception as e:
            print(f"Error deleting call list entries: {e}")
        
        # 9. Update events created by this user to set created_by to None
        event_update_count = Event.query.filter_by(created_by=user_id).update({'created_by': None})
        print(f"Updated {event_update_count} events")
        
        # 10. Update event attachments uploaded by this user to set uploaded_by to None
        try:
            attachment_update_count = EventAttachment.query.filter_by(uploaded_by=user_id).update({'uploaded_by': None})
            print(f"Updated {attachment_update_count} event attachments")
        except Exception as e:
            print(f"Error updating event attachments: {e}")
        
        # 11. Update event surveys created by this user to set created_by to None
        try:
            survey_update_count = EventSurvey.query.filter_by(created_by=user_id).update({'created_by': None})
            print(f"Updated {survey_update_count} event surveys")
        except Exception as e:
            print(f"Error updating event surveys: {e}")
        
        # 12. Update message threads created by this user to set created_by to None
        try:
            thread_update_count = MessageThread.query.filter_by(created_by=user_id).update({'created_by': None})
            print(f"Updated {thread_update_count} message threads")
        except Exception as e:
            print(f"Error updating message threads: {e}")
        
        # 13. Update messages sent by this user to set sender_id to None
        try:
            message_update_count = Message.query.filter_by(sender_id=user_id).update({'sender_id': None})
            print(f"Updated {message_update_count} messages")
        except Exception as e:
            print(f"Error updating messages: {e}")
        
        # 14. Handle additional models that might exist but aren't imported
        try:
            # Try to handle any other models that might reference the user
            from models import (
                EventCustomField, OrganizationEmailAlias, EmailForwardingRule,
                SectionMembership, PollResponse
            )
            
            # Update email forwarding rules
            EmailForwardingRule.query.filter_by(user_id=user_id).update({'user_id': None})
            
            # Delete section memberships
            SectionMembership.query.filter_by(user_id=user_id).delete()
            
            # Delete poll responses
            PollResponse.query.filter_by(user_id=user_id).delete()
            
            print("Handled additional models")
            
        except ImportError as e:
            print(f"Some models not available: {e}")
        except Exception as e:
            print(f"Error handling additional models: {e}")
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        print(f"Successfully deleted user {user_id}")
        return jsonify({'msg': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        error_message = f'Failed to delete user: {str(e)}'
        print(f"Error deleting user: {error_message}")
        return jsonify({'error': error_message}), 500


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
            'name': org.name or '',
            'logo_url': org.logo_url or '',
            'theme_color': org.theme_color or '#007bff',
            'rehearsal_address': org.rehearsal_address or '',
            'contact_phone': org.contact_phone or '',
            'contact_email': org.contact_email or '',
            'website': org.website or '',
            'facebook_url': org.facebook_url or '',
            'instagram_url': org.instagram_url or '',
            'twitter_url': org.twitter_url or '',
            'tiktok_url': org.tiktok_url or ''
        })
    if request.method == 'PUT':
        data = request.get_json()
        if 'name' in data and data['name']:
            org.name = data['name']
        if 'logo_url' in data:
            org.logo_url = data['logo_url']
        if 'theme_color' in data and data['theme_color']:
            org.theme_color = data['theme_color']
        if 'rehearsal_address' in data:
            org.rehearsal_address = data['rehearsal_address']
        if 'contact_phone' in data:
            org.contact_phone = data['contact_phone']
        if 'contact_email' in data:
            org.contact_email = data['contact_email']
        if 'website' in data:
            org.website = data['website']
        if 'facebook_url' in data:
            org.facebook_url = data['facebook_url']
        if 'instagram_url' in data:
            org.instagram_url = data['instagram_url']
        if 'twitter_url' in data:
            org.twitter_url = data['twitter_url']
        if 'tiktok_url' in data:
            org.tiktok_url = data['tiktok_url']
        
        db.session.commit()
        return jsonify({
            'msg': 'Organization updated',
            'name': org.name or '',
            'logo_url': org.logo_url or '',
            'theme_color': org.theme_color or '#007bff',
            'rehearsal_address': org.rehearsal_address or '',
            'contact_phone': org.contact_phone or '',
            'contact_email': org.contact_email or '',
            'website': org.website or '',
            'facebook_url': org.facebook_url or '',
            'instagram_url': org.instagram_url or '',
            'twitter_url': org.twitter_url or '',
            'tiktok_url': org.tiktok_url or ''
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
            organization_id=org_id,  # Legacy field
            current_organization_id=org_id,  # Current organization context
            primary_organization_id=org_id,  # Primary organization
            section_id=data.get('section_id')
        )
        
        # Set password (either provided or generate temporary)
        provided_password = data.get('password', '').strip()
        if provided_password:
            password = provided_password
        else:
            # Generate temporary password if none provided or empty
            password = f"temp_{data['username']}123"
        
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush()  # Flush to get the user ID
        
        # Create UserOrganization entry for multi-organization support
        user_org = UserOrganization(
            user_id=new_user.id,
            organization_id=org_id,
            role=data.get('role', 'Member'),
            section_id=data.get('section_id'),
            is_active=True
        )
        
        db.session.add(user_org)
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
            'temporary_password': password if not provided_password else None
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
    
    # Find user through UserOrganization relationship
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id,
        is_active=True
    ).first_or_404()
    
    user = user_org.user
    
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

@admin_bp.route('/users/add-existing', methods=['POST'])
@jwt_required()
def add_existing_user_to_organization():
    """Add an existing user to the current organization"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    data = request.get_json()
    org_id = claims.get('organization_id')
    
    # Validate required fields
    if not data.get('username') and not data.get('email'):
        return jsonify({'error': 'Username or email is required'}), 400
    
    try:
        # Find the existing user by username or email
        existing_user = None
        if data.get('username'):
            existing_user = User.query.filter_by(username=data['username']).first()
        elif data.get('email'):
            existing_user = User.query.filter_by(email=data['email']).first()
        
        if not existing_user:
            return jsonify({'error': 'User not found. Please check the username or email.'}), 404
        
        # Check if user is already in this organization
        existing_membership = UserOrganization.query.filter_by(
            user_id=existing_user.id,
            organization_id=org_id
        ).first()
        
        if existing_membership:
            if existing_membership.is_active:
                return jsonify({'error': 'User is already a member of this organization'}), 400
            else:
                # Reactivate the membership
                existing_membership.is_active = True
                existing_membership.role = data.get('role', 'Member')
                existing_membership.section_id = data.get('section_id')
                db.session.commit()
                
                return jsonify({
                    'msg': 'User re-added to organization successfully',
                    'user': {
                        'id': existing_user.id,
                        'username': existing_user.username,
                        'email': existing_user.email,
                        'name': existing_user.name,
                        'role': existing_membership.role
                    }
                }), 200
        
        # Add user to organization
        user_org = UserOrganization(
            user_id=existing_user.id,
            organization_id=org_id,
            role=data.get('role', 'Member'),
            section_id=data.get('section_id'),
            is_active=True
        )
        
        db.session.add(user_org)
        db.session.commit()
        
        # Send invitation email if requested
        if data.get('send_invitation', False):
            try:
                # Generate a temporary password
                temp_password = f"temp_{existing_user.username}123"
                existing_user.set_password(temp_password)
                db.session.commit()
                
                email_sent = send_invitation_email(existing_user, temp_password)
                if not email_sent:
                    print(f"Warning: Failed to send invitation email to {existing_user.email}")
            except Exception as e:
                print(f"Error sending invitation email: {str(e)}")
                # Don't fail the user addition if email fails
        
        return jsonify({
            'msg': 'User added to organization successfully',
            'user': {
                'id': existing_user.id,
                'username': existing_user.username,
                'email': existing_user.email,
                'name': existing_user.name,
                'role': user_org.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add user to organization: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    
    # Find user through UserOrganization relationship
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id,
        is_active=True
    ).first_or_404()
    
    u = user_org.user
    return jsonify({
        'id': u.id,
        'username': u.username,
        'name': u.name,
        'email': u.email,
        'phone': u.phone,
        'address': u.address,
        'role': user_org.role,  # Use role from UserOrganization
        'avatar_url': u.avatar_url,
        'section_id': user_org.section_id,  # Use section from UserOrganization
        'section_name': user_org.section.name if user_org.section else None
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
    
    # Get user through UserOrganization table
    user_org = UserOrganization.query.filter_by(
        user_id=user_id, 
        organization_id=org_id, 
        is_active=True
    ).first()
    if not user_org:
        return jsonify({'error': 'User not found'}), 404
    
    user = user_org.user
    
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
        from flask_jwt_extended import get_jwt
        
        # Get the current admin user who is sending the invitation
        current_user_id = get_jwt_identity()
        inviting_admin = User.query.get(current_user_id)
        
        if not inviting_admin:
            print(f"Warning: Could not find admin user with ID {current_user_id}")
            return False
        
        # Get the organization from JWT context
        claims = get_jwt()
        org_id = claims.get('organization_id')
        organization = Organization.query.get(org_id)
        
        if not organization:
            print(f"Warning: Could not find organization with ID {org_id}")
            return False
        
        # Send the invitation email using the proper email service
        success = email_service.send_user_invitation(user, password, inviting_admin, organization)
        
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
    
    users_data = []
    
    # Get users through UserOrganization table (multi-org users)
    user_orgs = UserOrganization.query.filter_by(organization_id=org_id, is_active=True).all()
    user_ids_from_org_table = set()
    
    for user_org in user_orgs:
        u = user_org.user
        user_ids_from_org_table.add(u.id)
        user_data = {
            'id': u.id,
            'username': u.username,
            'name': u.name or u.username,
            'display_name': u.name or u.username,
            'section_id': u.section_id,
            'section_name': u.section.name if u.section else None
        }
        users_data.append(user_data)
    
    # Also get legacy users (those with organization_id field set but not in UserOrganization)
    legacy_users = User.query.filter_by(organization_id=org_id).all()
    for u in legacy_users:
        if u.id not in user_ids_from_org_table:  # Don't duplicate users
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
        
        # Verify user exists and belongs to the organization
        user_org = UserOrganization.query.filter_by(
            user_id=user_id, 
            organization_id=org_id, 
            is_active=True
        ).first()
        if not user_org:
            return jsonify({'error': 'User not found'}), 404
        
        user = user_org.user
        
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
