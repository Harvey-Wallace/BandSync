"""
Activity Feed Backend - Tracks and broadcasts member activities
Integrates with existing WebSocket notification system
"""

from datetime import datetime, timezone
from flask import request
from functools import wraps
import json

class ActivityTracker:
    """Tracks and manages member activities for real-time feed"""
    
    def __init__(self, db, notification_manager):
        self.db = db
        self.notification_manager = notification_manager
        self.activity_types = {
            'user_joined': {
                'icon': '🟢',
                'template': '{user} joined the organization',
                'priority': 'low'
            },
            'user_login': {
                'icon': '👋',
                'template': '{user} logged in',
                'priority': 'low'
            },
            'event_created': {
                'icon': '📅',
                'template': '{user} created event "{event_title}"',
                'priority': 'high'
            },
            'event_updated': {
                'icon': '✏️',
                'template': '{user} updated event "{event_title}"',
                'priority': 'medium'
            },
            'event_cancelled': {
                'icon': '❌',
                'template': '{user} cancelled event "{event_title}"',
                'priority': 'high'
            },
            'rsvp_confirmed': {
                'icon': '✅',
                'template': '{user} confirmed attendance for "{event_title}"',
                'priority': 'medium'
            },
            'rsvp_declined': {
                'icon': '❌',
                'template': '{user} declined "{event_title}"',
                'priority': 'medium'
            },
            'rsvp_maybe': {
                'icon': '❓',
                'template': '{user} marked maybe for "{event_title}"',
                'priority': 'low'
            },
            'substitute_requested': {
                'icon': '🔄',
                'template': '{user} requested substitute for "{event_title}"',
                'priority': 'high'
            },
            'substitute_offered': {
                'icon': '🙋',
                'template': '{user} offered to substitute for "{event_title}"',
                'priority': 'high'
            },
            'profile_updated': {
                'icon': '👤',
                'template': '{user} updated their profile',
                'priority': 'low'
            },
            'member_promoted': {
                'icon': '⭐',
                'template': '{user} was promoted to {role}',
                'priority': 'medium'
            },
            'template_created': {
                'icon': '📋',
                'template': '{user} created template "{template_name}"',
                'priority': 'low'
            }
        }
    
    def track_activity(self, activity_type, user_id, organization_id, **kwargs):
        """Track a new activity and broadcast it"""
        try:
            # Get user info
            from models import User
            user = User.query.get(user_id)
            if not user:
                print(f"User {user_id} not found for activity tracking")
                return
            
            # Get activity config
            if activity_type not in self.activity_types:
                print(f"Unknown activity type: {activity_type}")
                return
            
            activity_config = self.activity_types[activity_type]
            
            # Format activity message
            format_data = {
                'user': user.name or user.username,
                **kwargs
            }
            
            message = activity_config['template'].format(**format_data)
            
            # Create activity data
            activity_data = {
                'id': f"{activity_type}_{user_id}_{int(datetime.now().timestamp())}",
                'type': activity_type,
                'user_id': user_id,
                'user_name': user.name or user.username,
                'user_avatar': user.avatar_url,
                'organization_id': organization_id,
                'message': message,
                'icon': activity_config['icon'],
                'priority': activity_config['priority'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': kwargs
            }
            
            # Store activity in database (optional - for history)
            self._store_activity(activity_data)
            
            # Broadcast to organization members
            self.notification_manager.broadcast_to_organization(
                organization_id=organization_id,
                event_type='member_activity',
                data={
                    'activity': activity_data,
                    'message': f"{activity_config['icon']} {message}"
                }
            )
            
            print(f"Activity tracked: {activity_type} by {user.username}")
            return activity_data
            
        except Exception as e:
            print(f"Error tracking activity {activity_type}: {str(e)}")
            return None
    
    def _store_activity(self, activity_data):
        """Store activity in database for history (optional)"""
        try:
            # For now, we'll keep activities in memory/broadcast only
            # Future: Create Activity model for persistent storage
            pass
        except Exception as e:
            print(f"Error storing activity: {str(e)}")
    
    def get_recent_activities(self, organization_id, limit=50):
        """Get recent activities for an organization"""
        try:
            # For now return empty - future: query from database
            # This would be used for initial feed load
            return []
        except Exception as e:
            print(f"Error getting recent activities: {str(e)}")
            return []

# Activity tracking decorator
def track_activity(activity_type, **track_kwargs):
    """Decorator to automatically track activities"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            try:
                # Get current user and organization from Flask context
                from flask_jwt_extended import get_jwt_identity
                from models import User
                
                current_user_id = get_jwt_identity()
                if not current_user_id:
                    return result
                
                user = User.query.get(current_user_id)
                if not user or not user.organization_id:
                    return result
                
                # Extract tracking data from function result or kwargs
                tracking_data = {}
                
                # If result is a tuple (response, status_code), extract data
                if isinstance(result, tuple) and len(result) >= 2:
                    response_data = result[0]
                    if hasattr(response_data, 'get_json'):
                        json_data = response_data.get_json()
                        if json_data:
                            tracking_data.update(json_data)
                
                # Merge with provided tracking kwargs
                tracking_data.update(track_kwargs)
                
                # Get activity tracker from app context
                from flask import current_app
                if hasattr(current_app, 'activity_tracker'):
                    current_app.activity_tracker.track_activity(
                        activity_type=activity_type,
                        user_id=current_user_id,
                        organization_id=user.organization_id,
                        **tracking_data
                    )
                
            except Exception as e:
                print(f"Error in activity tracking decorator: {str(e)}")
            
            return result
        
        return wrapper
    return decorator

# Manual activity tracking functions
def track_user_login(user_id, organization_id):
    """Track user login activity"""
    from flask import current_app
    if hasattr(current_app, 'activity_tracker'):
        current_app.activity_tracker.track_activity(
            'user_login', user_id, organization_id
        )

def track_rsvp_update(user_id, organization_id, event_title, rsvp_status):
    """Track RSVP status change"""
    from flask import current_app
    if hasattr(current_app, 'activity_tracker'):
        activity_type = f"rsvp_{rsvp_status.lower()}"
        if activity_type in current_app.activity_tracker.activity_types:
            current_app.activity_tracker.track_activity(
                activity_type, user_id, organization_id, event_title=event_title
            )

def track_event_action(user_id, organization_id, action, event_title):
    """Track event-related actions"""
    from flask import current_app
    if hasattr(current_app, 'activity_tracker'):
        activity_type = f"event_{action}"
        current_app.activity_tracker.track_activity(
            activity_type, user_id, organization_id, event_title=event_title
        )
