"""
Calendar API routes for BandSync
Provides iCal feeds and calendar integration endpoints.
"""

from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.calendar_service import calendar_service
from models import User, Organization, Section, UserOrganization
import logging

logger = logging.getLogger(__name__)

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/org/<int:org_id>/events.ics')
def organization_calendar(org_id):
    """
    Generate iCal feed for organization events
    
    Args:
        org_id: Organization ID
        
    Query Parameters:
        include_templates: Include template events (default: false)
    """
    try:
        include_templates = request.args.get('include_templates', 'false').lower() == 'true'
        
        # Generate calendar
        ical_data = calendar_service.generate_organization_calendar(
            org_id, 
            include_templates=include_templates
        )
        
        # Get organization name for filename
        org = Organization.query.get(org_id)
        filename = f"{org.name.replace(' ', '_')}_calendar.ics" if org else "calendar.ics"
        
        return Response(
            ical_data,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating organization calendar: {e}")
        return Response(
            "Error generating calendar",
            status=500,
            mimetype='text/plain'
        )

@calendar_bp.route('/user/<int:user_id>/org/<int:org_id>/events.ics')
def user_calendar(user_id, org_id):
    """
    Generate iCal feed for user's events in an organization
    
    Args:
        user_id: User ID
        org_id: Organization ID
    """
    try:
        # Generate calendar
        ical_data = calendar_service.generate_user_calendar(user_id, org_id)
        
        # Get user and org names for filename
        user = User.query.get(user_id)
        org = Organization.query.get(org_id)
        
        username = (user.name or user.username).replace(' ', '_') if user else 'user'
        orgname = org.name.replace(' ', '_') if org else 'organization'
        filename = f"{orgname}_{username}_calendar.ics"
        
        return Response(
            ical_data,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating user calendar: {e}")
        return Response(
            "Error generating calendar",
            status=500,
            mimetype='text/plain'
        )

@calendar_bp.route('/section/<int:section_id>/events.ics')
def section_calendar(section_id):
    """
    Generate iCal feed for section events
    
    Args:
        section_id: Section ID
    """
    try:
        # Generate calendar
        ical_data = calendar_service.generate_section_calendar(section_id)
        
        # Get section name for filename
        section = Section.query.get(section_id)
        if section:
            filename = f"{section.organization.name.replace(' ', '_')}_{section.name.replace(' ', '_')}_calendar.ics"
        else:
            filename = "section_calendar.ics"
        
        return Response(
            ical_data,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating section calendar: {e}")
        return Response(
            "Error generating calendar",
            status=500,
            mimetype='text/plain'
        )

@calendar_bp.route('/public/<int:org_id>/events.ics')
def public_calendar(org_id):
    """
    Generate public iCal feed for organization events
    
    Args:
        org_id: Organization ID
    """
    try:
        # Generate calendar
        ical_data = calendar_service.generate_public_calendar(org_id)
        
        # Get organization name for filename
        org = Organization.query.get(org_id)
        filename = f"{org.name.replace(' ', '_')}_public_calendar.ics" if org else "public_calendar.ics"
        
        return Response(
            ical_data,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'public, max-age=3600',  # Cache public calendars for 1 hour
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating public calendar: {e}")
        return Response(
            "Error generating calendar",
            status=500,
            mimetype='text/plain'
        )

@calendar_bp.route('/subscription-info')
@jwt_required()
def get_subscription_info():
    """
    Get calendar subscription information for the current user
    
    Returns:
        JSON with calendar subscription URLs and information
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        if not org_id:
            return jsonify({'error': 'Organization context required'}), 400
        
        # Get subscription info
        info = calendar_service.get_calendar_subscription_info(org_id, user_id)
        
        return jsonify({
            'success': True,
            'calendars': info,
            'instructions': {
                'google': 'Copy the calendar URL and paste it into Google Calendar > Add Calendar > From URL',
                'outlook': 'Copy the calendar URL and paste it into Outlook > Add Calendar > From Internet',
                'apple': 'Copy the calendar URL and paste it into Calendar > File > New Calendar Subscription',
                'general': 'Most calendar applications support subscribing to iCal feeds using the URLs provided'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}")
        return jsonify({'error': 'Failed to get subscription info'}), 500

@calendar_bp.route('/sync-settings', methods=['GET'])
@jwt_required()
def get_sync_settings():
    """
    Get calendar sync settings for the current user
    
    Returns:
        JSON with current sync settings
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Add calendar sync settings to user model
        # For now, return default settings
        settings = {
            'calendar_sync_enabled': True,
            'sync_reminders': True,
            'sync_all_events': True,
            'sync_rsvp_status': True,
            'default_calendar': 'primary'
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"Error getting sync settings: {e}")
        return jsonify({'error': 'Failed to get sync settings'}), 500

@calendar_bp.route('/sync-settings', methods=['PUT'])
@jwt_required()
def update_sync_settings():
    """
    Update calendar sync settings for the current user
    
    Body:
        JSON with sync settings to update
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Update user's calendar sync settings
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': 'Calendar sync settings updated'
        })
        
    except Exception as e:
        logger.error(f"Error updating sync settings: {e}")
        return jsonify({'error': 'Failed to update sync settings'}), 500

@calendar_bp.route('/test-feed/<int:org_id>')
@jwt_required()
def test_calendar_feed(org_id):
    """
    Test calendar feed generation (admin only)
    
    Args:
        org_id: Organization ID
    """
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Generate test calendar
        ical_data = calendar_service.generate_organization_calendar(org_id)
        
        # Count events
        event_count = ical_data.count(b'BEGIN:VEVENT')
        
        return jsonify({
            'success': True,
            'message': f'Calendar feed generated successfully with {event_count} events',
            'feed_size': len(ical_data),
            'sample_data': ical_data[:500].decode('utf-8', errors='ignore')
        })
        
    except Exception as e:
        logger.error(f"Error testing calendar feed: {e}")
        return jsonify({'error': f'Failed to test calendar feed: {str(e)}'}), 500

@calendar_bp.route('/widget/<int:org_id>')
def calendar_widget(org_id):
    """
    Generate embeddable calendar widget HTML
    
    Args:
        org_id: Organization ID
        
    Query Parameters:
        theme: Widget theme (light/dark)
        height: Widget height in pixels
        width: Widget width in pixels
    """
    try:
        theme = request.args.get('theme', 'light')
        height = request.args.get('height', '400')
        width = request.args.get('width', '100%')
        
        # Get organization
        org = Organization.query.get(org_id)
        if not org:
            return Response("Organization not found", status=404, mimetype='text/plain')
        
        # Generate widget HTML
        widget_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{org.name} Calendar</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 10px;
                    background-color: {'#ffffff' if theme == 'light' else '#2c3e50'};
                    color: {'#333333' if theme == 'light' else '#ecf0f1'};
                }}
                .calendar-widget {{
                    height: {height}px;
                    width: {width};
                    overflow-y: auto;
                    border: 1px solid {'#ddd' if theme == 'light' else '#555'};
                    border-radius: 4px;
                    padding: 10px;
                }}
                .calendar-header {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    text-align: center;
                }}
                .event-item {{
                    padding: 8px;
                    margin-bottom: 8px;
                    border-left: 4px solid {org.theme_color or '#007bff'};
                    background-color: {'#f8f9fa' if theme == 'light' else '#34495e'};
                    border-radius: 4px;
                }}
                .event-title {{
                    font-weight: bold;
                    margin-bottom: 4px;
                }}
                .event-date {{
                    font-size: 14px;
                    color: {'#666' if theme == 'light' else '#bdc3c7'};
                }}
                .calendar-footer {{
                    text-align: center;
                    margin-top: 15px;
                    font-size: 12px;
                    color: {'#999' if theme == 'light' else '#95a5a6'};
                }}
            </style>
        </head>
        <body>
            <div class="calendar-widget">
                <div class="calendar-header">{org.name} Events</div>
                <div id="events-container">
                    Loading events...
                </div>
                <div class="calendar-footer">
                    Powered by BandSync
                </div>
            </div>
            
            <script>
                // Load events via JavaScript
                fetch('/api/events?organization_id={org_id}')
                    .then(response => response.json())
                    .then(events => {{
                        const container = document.getElementById('events-container');
                        if (events.length === 0) {{
                            container.innerHTML = '<p>No upcoming events</p>';
                            return;
                        }}
                        
                        const now = new Date();
                        const upcomingEvents = events
                            .filter(event => new Date(event.date) >= now)
                            .sort((a, b) => new Date(a.date) - new Date(b.date))
                            .slice(0, 10);
                        
                        container.innerHTML = upcomingEvents.map(event => `
                            <div class="event-item">
                                <div class="event-title">${{event.title}}</div>
                                <div class="event-date">${{new Date(event.date).toLocaleDateString()}}</div>
                            </div>
                        `).join('');
                    }})
                    .catch(error => {{
                        document.getElementById('events-container').innerHTML = '<p>Error loading events</p>';
                    }});
            </script>
        </body>
        </html>
        """
        
        return Response(
            widget_html,
            mimetype='text/html',
            headers={
                'Cache-Control': 'public, max-age=3600',
                'X-Frame-Options': 'SAMEORIGIN'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating calendar widget: {e}")
        return Response(
            "Error generating calendar widget",
            status=500,
            mimetype='text/plain'
        )
