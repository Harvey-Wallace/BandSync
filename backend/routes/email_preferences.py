"""
Email preferences management routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
import secrets

email_prefs_bp = Blueprint('email_prefs', __name__)

@email_prefs_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_email_preferences():
    """Get current user's email preferences"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'email_notifications': user.email_notifications,
        'email_event_reminders': user.email_event_reminders,
        'email_new_events': user.email_new_events,
        'email_rsvp_reminders': user.email_rsvp_reminders,
        'email_daily_summary': user.email_daily_summary,
        'email_weekly_summary': user.email_weekly_summary,
        'email_substitute_requests': user.email_substitute_requests,
        'email_admin_attendance_reports': user.email_admin_attendance_reports,
        'admin_attendance_report_timing': user.admin_attendance_report_timing,
        'admin_attendance_report_unit': user.admin_attendance_report_unit,
        'email_admin_rsvp_changes': user.email_admin_rsvp_changes,
        'is_admin': user.role == 'admin'
    })

@email_prefs_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_email_preferences():
    """Update user's email preferences"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update preferences
    if 'email_notifications' in data:
        user.email_notifications = data['email_notifications']
    if 'email_event_reminders' in data:
        user.email_event_reminders = data['email_event_reminders']
    if 'email_new_events' in data:
        user.email_new_events = data['email_new_events']
    if 'email_rsvp_reminders' in data:
        user.email_rsvp_reminders = data['email_rsvp_reminders']
    if 'email_daily_summary' in data:
        user.email_daily_summary = data['email_daily_summary']
    if 'email_weekly_summary' in data:
        user.email_weekly_summary = data['email_weekly_summary']
    if 'email_substitute_requests' in data:
        user.email_substitute_requests = data['email_substitute_requests']
    
    # Admin attendance notification preferences (only for admins)
    if user.role == 'admin':
        if 'email_admin_attendance_reports' in data:
            user.email_admin_attendance_reports = data['email_admin_attendance_reports']
        if 'admin_attendance_report_timing' in data:
            user.admin_attendance_report_timing = data['admin_attendance_report_timing']
        if 'admin_attendance_report_unit' in data:
            user.admin_attendance_report_unit = data['admin_attendance_report_unit']
        if 'email_admin_rsvp_changes' in data:
            user.email_admin_rsvp_changes = data['email_admin_rsvp_changes']
    
    db.session.commit()
    
    return jsonify({'message': 'Email preferences updated successfully'})

@email_prefs_bp.route('/unsubscribe/<token>', methods=['GET'])
def unsubscribe_user(token):
    """Unsubscribe user from all emails using unsubscribe token"""
    user = User.query.filter_by(unsubscribe_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid unsubscribe token'}), 404
    
    # Turn off all email notifications
    user.email_notifications = False
    user.email_event_reminders = False
    user.email_new_events = False
    user.email_rsvp_reminders = False
    user.email_daily_summary = False
    user.email_weekly_summary = False
    user.email_substitute_requests = False
    
    db.session.commit()
    
    return jsonify({'message': 'Successfully unsubscribed from all email notifications'})

@email_prefs_bp.route('/generate-unsubscribe-token', methods=['POST'])
@jwt_required()
def generate_unsubscribe_token():
    """Generate an unsubscribe token for the current user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate secure token
    if not user.unsubscribe_token:
        user.unsubscribe_token = secrets.token_urlsafe(32)
        db.session.commit()
    
    return jsonify({'unsubscribe_token': user.unsubscribe_token})

@email_prefs_bp.route('/admin/attendance-timing-options', methods=['GET'])
@jwt_required()
def get_attendance_timing_options():
    """Get available timing options for admin attendance reports"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    from services.admin_attendance_service import AdminAttendanceService
    options = AdminAttendanceService.get_timing_options()
    
    return jsonify({'timing_options': options})

@email_prefs_bp.route('/test-email', methods=['POST'])
@jwt_required()
def send_test_email():
    """Send a test email to the current user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        from services.email_service import EmailService
        email_service = EmailService()
        
        # Send test email
        success = email_service._send_email(
            to_emails=[user.email],
            subject="BandSync Test Email",
            html_content=f"""
            <h2>Test Email</h2>
            <p>Hello {user.name or user.username},</p>
            <p>This is a test email from BandSync to verify your email settings are working correctly.</p>
            <p>If you received this email, your email notifications are configured properly.</p>
            <br>
            <p>Best regards,<br>The BandSync Team</p>
            """,
            text_content=f"Hello {user.name or user.username}, This is a test email from BandSync."
        )
        
        if success:
            return jsonify({'message': 'Test email sent successfully'})
        else:
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to send test email: {str(e)}'}), 500
