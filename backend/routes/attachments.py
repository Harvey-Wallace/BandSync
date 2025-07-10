from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Event, EventAttachment
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

attachments_bp = Blueprint('attachments', __name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/attachments'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
    'jpg', 'jpeg', 'png', 'gif', 'bmp',  # Images
    'mp3', 'wav', 'ogg', 'flac',  # Audio
    'mp4', 'avi', 'mov', 'wmv',  # Video
    'zip', 'rar', '7z',  # Archives
    'mid', 'midi', 'musicxml', 'xml'  # Music files
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    """Get file size in bytes"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

@attachments_bp.route('/api/events/<int:event_id>/attachments', methods=['GET'])
@jwt_required()
def get_event_attachments(event_id):
    """Get attachments for an event"""
    try:
        event = Event.query.get_or_404(event_id)
        attachments = EventAttachment.query.filter_by(event_id=event_id).order_by(EventAttachment.created_at.desc()).all()
        
        attachments_data = []
        for attachment in attachments:
            attachment_data = {
                'id': attachment.id,
                'filename': attachment.filename,
                'original_filename': attachment.original_filename,
                'file_size': attachment.file_size,
                'file_type': attachment.file_type,
                'description': attachment.description,
                'is_public': attachment.is_public,
                'uploaded_by': {
                    'id': attachment.uploader.id,
                    'username': attachment.uploader.username,
                    'name': attachment.uploader.name
                },
                'created_at': attachment.created_at.isoformat(),
                'download_url': f'/api/events/{event_id}/attachments/{attachment.id}/download'
            }
            attachments_data.append(attachment_data)
        
        return jsonify(attachments_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attachments_bp.route('/api/events/<int:event_id>/attachments', methods=['POST'])
@jwt_required()
def upload_attachment(event_id):
    """Upload a file attachment to an event"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        event = Event.query.get_or_404(event_id)
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large (max 10MB)'}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Create attachment record
        attachment = EventAttachment(
            event_id=event_id,
            filename=unique_filename,
            original_filename=original_filename,
            file_url=f'/uploads/attachments/{unique_filename}',
            file_size=file_size,
            file_type=file.content_type,
            description=request.form.get('description', ''),
            uploaded_by=user.id,
            is_public=request.form.get('is_public', 'true').lower() == 'true'
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'filename': attachment.filename,
            'original_filename': attachment.original_filename,
            'file_size': attachment.file_size,
            'file_type': attachment.file_type,
            'description': attachment.description,
            'is_public': attachment.is_public,
            'uploaded_by': {
                'id': user.id,
                'username': user.username,
                'name': user.name
            },
            'created_at': attachment.created_at.isoformat(),
            'download_url': f'/api/events/{event_id}/attachments/{attachment.id}/download'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attachments_bp.route('/api/events/<int:event_id>/attachments/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(event_id, attachment_id):
    """Delete an attachment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        attachment = EventAttachment.query.get_or_404(attachment_id)
        if attachment.event_id != event_id:
            return jsonify({'error': 'Attachment does not belong to this event'}), 400
        
        # Check permissions (admin or uploader can delete)
        if user.role != 'Admin' and attachment.uploaded_by != user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Delete physical file
        file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, attachment.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.session.delete(attachment)
        db.session.commit()
        
        return jsonify({'message': 'Attachment deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attachments_bp.route('/api/events/<int:event_id>/attachments/<int:attachment_id>/download', methods=['GET'])
@jwt_required()
def download_attachment(event_id, attachment_id):
    """Download an attachment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        attachment = EventAttachment.query.get_or_404(attachment_id)
        if attachment.event_id != event_id:
            return jsonify({'error': 'Attachment does not belong to this event'}), 400
        
        # Check if file is public or user has access
        if not attachment.is_public and user.role != 'Admin' and attachment.uploaded_by != user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Serve file
        file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, attachment.filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=attachment.original_filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attachments_bp.route('/api/events/<int:event_id>/attachments/<int:attachment_id>', methods=['PUT'])
@jwt_required()
def update_attachment(event_id, attachment_id):
    """Update attachment metadata"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        attachment = EventAttachment.query.get_or_404(attachment_id)
        if attachment.event_id != event_id:
            return jsonify({'error': 'Attachment does not belong to this event'}), 400
        
        # Check permissions (admin or uploader can update)
        if user.role != 'Admin' and attachment.uploaded_by != user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'description' in data:
            attachment.description = data['description']
        if 'is_public' in data:
            attachment.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'id': attachment.id,
            'filename': attachment.filename,
            'original_filename': attachment.original_filename,
            'file_size': attachment.file_size,
            'file_type': attachment.file_type,
            'description': attachment.description,
            'is_public': attachment.is_public,
            'uploaded_by': {
                'id': attachment.uploader.id,
                'username': attachment.uploader.username,
                'name': attachment.uploader.name
            },
            'created_at': attachment.created_at.isoformat(),
            'download_url': f'/api/events/{event_id}/attachments/{attachment.id}/download'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
