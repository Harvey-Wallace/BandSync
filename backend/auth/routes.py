from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import User, db, Organization
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
import os
from werkzeug.utils import secure_filename

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
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Username already exists'}), 400
    org_name = data.get('organization')
    if not org_name:
        return jsonify({'msg': 'Organization is required'}), 400
    org = Organization.query.filter_by(name=org_name).first()
    org_created = False
    if not org:
        # Create new org if not exists
        org = Organization(name=org_name)
        db.session.add(org)
        db.session.commit()
        org_created = True
    # If org was just created, first user is Admin
    if org_created:
        user_role = 'Admin'
    else:
        user_role = data.get('role', 'Member')
    user = User(
        username=data['username'],
        email=data['email'],
        role=user_role,
        organization_id=org.id
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User registered successfully', 'organization_id': org.id, 'organization': org.name})

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
