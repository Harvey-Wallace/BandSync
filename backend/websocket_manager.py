"""
WebSocket Manager for Real-time Notifications
Handles WebSocket connections and broadcasts notifications to connected clients
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import User, Organization
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected_users = {}  # {user_id: {socket_id: session_info}}
        self.user_organizations = {}  # {user_id: org_id}
        
    def get_connected_users_count(self):
        """Get total number of connected users"""
        return len(self.connected_users)
    
    def get_organization_members(self, org_id):
        """Get all connected users for an organization"""
        return [user_id for user_id, user_org_id in self.user_organizations.items() 
                if user_org_id == org_id and user_id in self.connected_users]
    
    def broadcast_to_organization(self, org_id, event_type, data):
        """Broadcast notification to all members of an organization"""
        members = self.get_organization_members(org_id)
        logger.info(f"Broadcasting {event_type} to {len(members)} members of org {org_id}")
        
        for user_id in members:
            user_sessions = self.connected_users.get(user_id, {})
            for socket_id in user_sessions:
                self.socketio.emit(event_type, data, room=socket_id)
    
    def send_to_user(self, user_id, event_type, data):
        """Send notification to a specific user"""
        user_sessions = self.connected_users.get(user_id, {})
        logger.info(f"Sending {event_type} to user {user_id} ({len(user_sessions)} sessions)")
        
        for socket_id in user_sessions:
            self.socketio.emit(event_type, data, room=socket_id)
    
    def user_connected(self, user_id, socket_id, user_data):
        """Handle user connection"""
        if user_id not in self.connected_users:
            self.connected_users[user_id] = {}
        
        self.connected_users[user_id][socket_id] = {
            'connected_at': datetime.utcnow().isoformat(),
            'username': user_data.get('username'),
            'organization_id': user_data.get('organization_id')
        }
        
        if user_data.get('organization_id'):
            self.user_organizations[user_id] = user_data['organization_id']
        
        # Join organization room
        if user_data.get('organization_id'):
            join_room(f"org_{user_data['organization_id']}", sid=socket_id)
        
        logger.info(f"User {user_id} connected with socket {socket_id}")
    
    def user_disconnected(self, user_id, socket_id):
        """Handle user disconnection"""
        if user_id in self.connected_users:
            self.connected_users[user_id].pop(socket_id, None)
            
            # Remove user entirely if no sessions left
            if not self.connected_users[user_id]:
                self.connected_users.pop(user_id, None)
                self.user_organizations.pop(user_id, None)
        
        logger.info(f"User {user_id} disconnected socket {socket_id}")

# Global notification manager instance
notification_manager = None

def init_websocket(app):
    """Initialize WebSocket with Flask app"""
    global notification_manager
    
    # Configure CORS for WebSocket
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    notification_manager = NotificationManager(socketio)
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        try:
            # Extract JWT token from auth
            token = auth.get('token') if auth else None
            if not token:
                logger.warning("No token provided in WebSocket connection")
                return False
            
            # Decode JWT token to get user info
            try:
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                
                # Get user details from database
                user = User.query.get(user_id)
                if not user:
                    logger.warning(f"User {user_id} not found")
                    return False
                
                user_data = {
                    'username': user.username,
                    'organization_id': user.organization_id,
                    'role': user.role
                }
                
                # Register user connection
                notification_manager.user_connected(user_id, request.sid, user_data)
                
                # Send connection confirmation
                emit('connection_confirmed', {
                    'status': 'connected',
                    'user_id': user_id,
                    'username': user.username,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Send initial notifications count or pending notifications
                emit('notification_status', {
                    'connected_users': notification_manager.get_connected_users_count(),
                    'organization_members_online': len(notification_manager.get_organization_members(user.organization_id))
                })
                
                logger.info(f"User {user.username} ({user_id}) connected successfully")
                return True
                
            except Exception as e:
                logger.error(f"Token decode error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            # Try to find user by socket ID (this is a simplified approach)
            socket_id = request.sid
            
            # Find and remove user
            for user_id, sessions in list(notification_manager.connected_users.items()):
                if socket_id in sessions:
                    notification_manager.user_disconnected(user_id, socket_id)
                    break
                    
            logger.info(f"Socket {socket_id} disconnected")
            
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}")
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for keepalive"""
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})
    
    return socketio

def get_notification_manager():
    """Get the global notification manager instance"""
    return notification_manager

# Notification event types
class NotificationTypes:
    RSVP_UPDATED = 'rsvp_updated'
    EVENT_CREATED = 'event_created'
    EVENT_UPDATED = 'event_updated'
    EVENT_CANCELLED = 'event_cancelled'
    MEMBER_JOINED = 'member_joined'
    MEMBER_LEFT = 'member_left'
    MESSAGE_RECEIVED = 'message_received'
    SUBSTITUTE_REQUESTED = 'substitute_requested'
    SUBSTITUTE_ACCEPTED = 'substitute_accepted'
    REMINDER_SENT = 'reminder_sent'

# Helper functions for sending notifications
def notify_rsvp_update(event_id, user_id, rsvp_status, event_title):
    """Send RSVP update notification"""
    if not notification_manager:
        return
    
    try:
        user = User.query.get(user_id)
        if not user:
            return
        
        notification_data = {
            'type': NotificationTypes.RSVP_UPDATED,
            'event_id': event_id,
            'user_id': user_id,
            'username': user.username,
            'rsvp_status': rsvp_status,
            'event_title': event_title,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"{user.username} {rsvp_status} for {event_title}"
        }
        
        # Broadcast to organization members
        notification_manager.broadcast_to_organization(
            user.organization_id, 
            NotificationTypes.RSVP_UPDATED, 
            notification_data
        )
        
        logger.info(f"RSVP notification sent: {user.username} {rsvp_status} for {event_title}")
        
    except Exception as e:
        logger.error(f"Error sending RSVP notification: {e}")

def notify_event_created(event_id, event_title, creator_id, organization_id):
    """Send event created notification"""
    if not notification_manager:
        return
    
    try:
        creator = User.query.get(creator_id)
        
        notification_data = {
            'type': NotificationTypes.EVENT_CREATED,
            'event_id': event_id,
            'event_title': event_title,
            'creator_username': creator.username if creator else 'Unknown',
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"New event created: {event_title}"
        }
        
        # Broadcast to organization members
        notification_manager.broadcast_to_organization(
            organization_id, 
            NotificationTypes.EVENT_CREATED, 
            notification_data
        )
        
        logger.info(f"Event created notification sent: {event_title}")
        
    except Exception as e:
        logger.error(f"Error sending event created notification: {e}")

def notify_event_updated(event_id, event_title, organization_id, changes):
    """Send event updated notification"""
    if not notification_manager:
        return
    
    try:
        notification_data = {
            'type': NotificationTypes.EVENT_UPDATED,
            'event_id': event_id,
            'event_title': event_title,
            'changes': changes,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"Event updated: {event_title}"
        }
        
        # Broadcast to organization members
        notification_manager.broadcast_to_organization(
            organization_id, 
            NotificationTypes.EVENT_UPDATED, 
            notification_data
        )
        
        logger.info(f"Event updated notification sent: {event_title}")
        
    except Exception as e:
        logger.error(f"Error sending event updated notification: {e}")
