from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import User, db, Organization
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
import os
from werkzeug.utils import secure_filename
from services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)

# Configure Cloudinary (you'll need to set these environment variables)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

@auth_bp.route('/update_email', methods=['PUT'])
@jwt_required()
def update_email():
    data = request.get_json()
    new_email = data.get('email')
    if not new_email:
        return jsonify({'msg': 'Email is required'}), 400
    if User.query.filter_by(email=new_email).first():
        return jsonify({'msg': 'Email already in use'}), 400
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    user.email = new_email
    db.session.commit()
    return jsonify({'msg': 'Email updated successfully'})

@auth_bp.route('/update_password', methods=['PUT'])
@jwt_required()
def update_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'msg': 'Current password and new password are required'}), 400
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    # Verify current password
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'msg': 'Current password is incorrect'}), 400
    
    # Update to new password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'msg': 'Password updated successfully'})

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'msg': 'No data provided'}), 400
            
        required_fields = ['username', 'email', 'password', 'organization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'{field} is required'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'msg': 'Username already exists'}), 400
            
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 400
        
        org_name = data.get('organization')
        
        # Find or create organization
        org = Organization.query.filter_by(name=org_name).first()
        org_created = False
        if not org:
            # Create new org if not exists
            org = Organization(name=org_name)
            db.session.add(org)
            db.session.flush()  # Flush to get the ID
            org_created = True
        
        # If org was just created, first user is Admin
        if org_created:
            user_role = 'Admin'
        else:
            user_role = data.get('role', 'Member')
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role=user_role,
            organization_id=org.id
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'msg': 'User registered successfully', 
            'organization_id': org.id, 
            'organization': org.name
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'msg': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Support both email and username login
    if 'email' in data:
        user = User.query.filter_by(email=data['email']).first()
    elif 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
    else:
        return jsonify({'msg': 'Email or username is required'}), 400
    
    if user and user.check_password(data['password']):
        from models import UserOrganization
        
        # Get all organizations user belongs to
        user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
        
        # If user requested a specific organization
        requested_org_id = data.get('organization_id')
        if requested_org_id:
            user_org = next((uo for uo in user_orgs if uo.organization_id == requested_org_id), None)
            if not user_org:
                return jsonify({'msg': 'You do not belong to the selected organization'}), 403
            
            selected_org = user_org.organization
            selected_role = user_org.role
            
            # Update current organization
            user.current_organization_id = requested_org_id
            db.session.commit()
        
        # If user belongs to multiple organizations and no specific org requested
        elif len(user_orgs) > 1:
            organizations = []
            for user_org in user_orgs:
                organizations.append({
                    'id': user_org.organization_id,
                    'name': user_org.organization.name,
                    'role': user_org.role
                })
            
            return jsonify({
                'multiple_organizations': True,
                'organizations': organizations
            })
        
        # Single organization or fallback
        else:
            if user_orgs:
                user_org = user_orgs[0]
                selected_org = user_org.organization
                selected_role = user_org.role
                
                # Update current organization
                user.current_organization_id = user_org.organization_id
                db.session.commit()
            else:
                # Fallback to legacy organization setup
                org_id = user.primary_organization_id or user.organization_id
                selected_org = Organization.query.get(org_id) if org_id else None
                selected_role = user.role
                
                if selected_org:
                    user.current_organization_id = org_id
                    db.session.commit()
        
        # Create tokens with organization context
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': selected_role,
                'organization_id': selected_org.id if selected_org else None,
                'organization': selected_org.name if selected_org else None
            }
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'role': selected_role,
            'organization_id': selected_org.id if selected_org else None,
            'organization': selected_org.name if selected_org else None
        })
    
    return jsonify({'msg': 'Invalid credentials'}), 401

@auth_bp.route('/update_avatar', methods=['PUT'])
@jwt_required()
def update_avatar():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    if not avatar_url:
        return jsonify({'msg': 'Avatar URL is required'}), 400
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    user.avatar_url = avatar_url
    db.session.commit()
    return jsonify({'msg': 'Avatar updated successfully', 'avatar_url': avatar_url})

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'role': user.role,
        'avatar_url': user.avatar_url,
        'organization_id': user.organization_id
    })

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    # Check if email is being changed and if it's already in use by another user
    if 'email' in data and data['email'] != user.email:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'msg': 'Email already in use'}), 400
    
    # Update profile fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    
    db.session.commit()
    return jsonify({'msg': 'Profile updated successfully'})

@auth_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    try:
        # Check if file is present in the request
        if 'file' not in request.files:
            return jsonify({'msg': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'msg': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'msg': 'Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed'}), 400
        
        # Get current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"bandsync/avatars/{user_id}",
            transformation=[
                {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
                {'quality': 'auto'},
                {'format': 'auto'}
            ]
        )
        
        # Update user's avatar URL
        user.avatar_url = upload_result['secure_url']
        db.session.commit()
        
        return jsonify({
            'msg': 'Avatar uploaded successfully',
            'avatar_url': upload_result['secure_url']
        })
        
    except Exception as e:
        return jsonify({'msg': f'Upload failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    org = Organization.query.get(user.organization_id)
    new_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user.role,
            'organization_id': user.organization_id,
            'organization': org.name if org else None
        }
    )
    
    return jsonify({
        'access_token': new_token,
        'role': user.role,
        'organization_id': user.organization_id,
        'organization': org.name if org else None
    })

@auth_bp.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    """Request a password reset email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'msg': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        if user:
            try:
                # Check if password reset columns exist
                if not hasattr(user, 'password_reset_token'):
                    return jsonify({'msg': 'Password reset temporarily unavailable. Please contact administrator.'}), 503
                
                # Generate password reset token
                token = user.generate_password_reset_token()
                db.session.commit()
                
                # Send password reset email
                from services.email_service import EmailService
                email_service = EmailService()
                
                if not email_service.client:
                    return jsonify({'msg': 'Email service not configured. Please contact administrator.'}), 503
                
                base_url = os.getenv('BASE_URL', 'http://localhost:3000')
                reset_url = f"{base_url}/reset-password?token={token}"
                
                # Get user's organization for context
                org = user.current_organization or user.primary_organization or user.organization
                org_name = org.name if org else 'BandSync'
                
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .logo {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                        .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
                        .button {{ display: inline-block; padding: 12px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                        .warning {{ color: #856404; background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🎵 BandSync</div>
                            <h1>Password Reset Request</h1>
                        </div>
                        
                        <div class="content">
                            <p>Hello <strong>{user.name or user.username}</strong>,</p>
                            
                            <p>You have requested to reset your password for your BandSync account in <strong>{org_name}</strong>.</p>
                            
                            <p>Click the button below to reset your password:</p>
                            
                            <div style="text-align: center;">
                                <a href="{reset_url}" class="button">Reset Password</a>
                            </div>
                            
                            <p>Or copy and paste this link into your browser:</p>
                            <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">{reset_url}</p>
                            
                            <div class="warning">
                                <strong>⚠️ Important:</strong>
                                <ul>
                                    <li>This link will expire in 1 hour</li>
                                    <li>If you didn't request this reset, please ignore this email</li>
                                    <li>For security, this link can only be used once</li>
                                </ul>
                            </div>
                            
                            <p>If you're having trouble with the link, you can request a new password reset from the login page.</p>
                        </div>
                        
                        <div class="footer">
                            <p>This email was sent by BandSync for {org_name}</p>
                            <p>If you have questions, please contact your organization administrator.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
                BandSync - Password Reset Request
                
                Hello {user.name or user.username},
                
                You have requested to reset your password for your BandSync account in {org_name}.
                
                Please visit the following link to reset your password:
                {reset_url}
                
                Important:
                - This link will expire in 1 hour
                - If you didn't request this reset, please ignore this email
                - For security, this link can only be used once
                
                If you're having trouble with the link, you can request a new password reset from the login page.
                
                This email was sent by BandSync for {org_name}.
                """
                
                success = email_service._send_email(
                    to_emails=[user.email],
                    subject=f"Password Reset - {org_name}",
                    html_content=html_content,
                    text_content=text_content
                )
                
                if not success:
                    print(f"Failed to send password reset email to {user.email}")
                    
            except Exception as e:
                print(f"Error sending password reset email: {e}")
                # Don't reveal the error to prevent information disclosure
                pass
        
        return jsonify({'msg': 'If an account with that email exists, a password reset link has been sent.'})
        
    except Exception as e:
        print(f"Password reset request error: {e}")
        return jsonify({'msg': 'An error occurred. Please try again later.'}), 500

@auth_bp.route('/password-reset', methods=['POST'])
def password_reset():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'msg': 'Token and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'msg': 'Password must be at least 6 characters long'}), 400
        
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return jsonify({'msg': 'Invalid or expired reset token'}), 400
        
        # Check if password reset columns exist
        if not hasattr(user, 'password_reset_token') or not hasattr(user, 'password_reset_expires'):
            return jsonify({'msg': 'Password reset temporarily unavailable. Please contact administrator.'}), 503
        
        if not user.verify_password_reset_token(token):
            return jsonify({'msg': 'Invalid or expired reset token'}), 400
        
        try:
            # Update password
            user.set_password(new_password)
            user.clear_password_reset_token()
            db.session.commit()
            
            # Send confirmation email
            from services.email_service import EmailService
            email_service = EmailService()
            
            if email_service.client:
                org = user.current_organization or user.primary_organization or user.organization
                org_name = org.name if org else 'BandSync'
                
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .logo {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                        .content {{ background: #f8f9fa; padding: 30px; border-radius: 8px; }}
                        .success {{ color: #155724; background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🎵 BandSync</div>
                            <h1>Password Reset Successful</h1>
                        </div>
                        
                        <div class="content">
                            <p>Hello <strong>{user.name or user.username}</strong>,</p>
                            
                            <div class="success">
                                <strong>✅ Success!</strong> Your password has been reset successfully.
                            </div>
                            
                            <p>Your password for your BandSync account in <strong>{org_name}</strong> has been changed.</p>
                            
                            <p>You can now log in with your new password.</p>
                            
                            <p>If you didn't make this change, please contact your organization administrator immediately.</p>
                        </div>
                        
                        <div class="footer">
                            <p>This email was sent by BandSync for {org_name}</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
                BandSync - Password Reset Successful
                
                Hello {user.name or user.username},
                
                Your password for your BandSync account in {org_name} has been changed successfully.
                
                You can now log in with your new password.
                
                If you didn't make this change, please contact your organization administrator immediately.
                
                This email was sent by BandSync for {org_name}.
                """
                
                email_service._send_email(
                    to_emails=[user.email],
                    subject=f"Password Reset Successful - {org_name}",
                    html_content=html_content,
                    text_content=text_content
                )
            
            return jsonify({'msg': 'Password reset successful. You can now log in with your new password.'})
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting password: {e}")
            return jsonify({'msg': 'An error occurred while resetting your password. Please try again.'}), 500
            
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({'msg': 'An error occurred. Please try again later.'}), 500
