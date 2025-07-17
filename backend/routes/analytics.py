"""
Analytics API Routes for BandSync
Provides admin analytics and insights endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from services.analytics_service import AnalyticsService
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

def admin_required():
    """Decorator to require admin access"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get organization overview analytics"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    days = request.args.get('days', 30, type=int)
    days = min(max(days, 1), 365)  # Limit between 1 and 365 days
    
    try:
        overview = AnalyticsService.get_organization_overview(user.organization_id, days)
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/members', methods=['GET'])
@jwt_required()
def get_member_analytics():
    """Get member engagement analytics"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    days = request.args.get('days', 30, type=int)
    days = min(max(days, 1), 365)  # Limit between 1 and 365 days
    
    try:
        member_analytics = AnalyticsService.get_member_analytics(user.organization_id, days)
        return jsonify(member_analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/events', methods=['GET'])
@jwt_required()
def get_event_analytics():
    """Get event performance analytics"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    days = request.args.get('days', 90, type=int)
    days = min(max(days, 1), 365)  # Limit between 1 and 365 days
    
    try:
        event_analytics = AnalyticsService.get_event_analytics(user.organization_id, days)
        return jsonify(event_analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/communication', methods=['GET'])
@jwt_required()
def get_communication_analytics():
    """Get communication and engagement analytics"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    days = request.args.get('days', 30, type=int)
    days = min(max(days, 1), 365)  # Limit between 1 and 365 days
    
    try:
        comm_analytics = AnalyticsService.get_communication_analytics(user.organization_id, days)
        return jsonify(comm_analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/health', methods=['GET'])
@jwt_required()
def get_organization_health():
    """Get organization health score and recommendations"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    try:
        health_data = AnalyticsService.get_organization_health_score(user.organization_id)
        return jsonify(health_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    try:
        # Get all analytics data for dashboard
        overview = AnalyticsService.get_organization_overview(user.organization_id, 30)
        member_analytics = AnalyticsService.get_member_analytics(user.organization_id, 30)
        event_analytics = AnalyticsService.get_event_analytics(user.organization_id, 90)
        comm_analytics = AnalyticsService.get_communication_analytics(user.organization_id, 30)
        health_data = AnalyticsService.get_organization_health_score(user.organization_id)
        
        dashboard_data = {
            'overview': overview,
            'member_summary': {
                'top_participants': member_analytics['top_participants'][:5],
                'section_stats': member_analytics['section_stats'],
                'inactive_count': member_analytics['inactive_count']
            },
            'event_summary': {
                'recent_events': event_analytics['event_stats'][:10],
                'type_stats': event_analytics['type_stats'],
                'monthly_trends': event_analytics['monthly_trends'][-6:]  # Last 6 months
            },
            'communication': comm_analytics,
            'health': health_data,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_analytics():
    """Export analytics data as CSV"""
    auth_check = admin_required()
    if auth_check:
        return auth_check
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    export_type = request.args.get('type', 'overview')
    days = request.args.get('days', 30, type=int)
    
    try:
        if export_type == 'members':
            data = AnalyticsService.get_member_analytics(user.organization_id, days)
            # Convert to CSV format
            csv_data = "Name,Username,Email,Section,Total RSVPs,Yes RSVPs,No RSVPs,Maybe RSVPs,Attendance Rate\n"
            for member in data['member_stats']:
                csv_data += f"{member['name']},{member['username']},{member['email']},{member.get('section_id', '')},{member['total_rsvps']},{member['yes_rsvps']},{member['no_rsvps']},{member['maybe_rsvps']},{member['attendance_rate']}%\n"
            
        elif export_type == 'events':
            data = AnalyticsService.get_event_analytics(user.organization_id, days)
            csv_data = "Title,Date,Type,Total Responses,Yes Count,No Count,Maybe Count,Attendance Rate\n"
            for event in data['event_stats']:
                csv_data += f"{event['title']},{event['date']},{event['event_type']},{event['total_responses']},{event['yes_count']},{event['no_count']},{event['maybe_count']},{event['attendance_rate']}%\n"
            
        else:  # overview
            data = AnalyticsService.get_organization_overview(user.organization_id, days)
            csv_data = "Metric,Value\n"
            for key, value in data.items():
                csv_data += f"{key.replace('_', ' ').title()},{value}\n"
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=analytics_{export_type}_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
