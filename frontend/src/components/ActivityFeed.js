/**
 * Live Member Activity Feed Component
 * Shows real-time member activities with scrollable feed
 */

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';
import UserAvatar from './UserAvatar';

const ActivityItem = ({ activity }) => {
  const getActivityIcon = (type) => {
    const icons = {
      'user_login': '👋',
      'user_joined': '🟢',
      'event_created': '📅',
      'event_updated': '✏️',
      'event_cancelled': '❌',
      'rsvp_confirmed': '✅',
      'rsvp_declined': '❌',
      'rsvp_maybe': '❓',
      'substitute_requested': '🔄',
      'substitute_offered': '🙋',
      'profile_updated': '👤',
      'member_promoted': '⭐',
      'template_created': '📋'
    };
    return icons[type] || '📢';
  };

  const getActivityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-danger';
      case 'medium': return 'text-warning';
      case 'low': return 'text-muted';
      default: return 'text-info';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - activityTime) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return activityTime.toLocaleDateString();
  };

  return (
    <div className="d-flex align-items-start mb-3 activity-item">
      <div className="flex-shrink-0 me-3">
        <UserAvatar 
          user={{ 
            name: activity.user_name, 
            avatar_url: activity.user_avatar 
          }} 
          size={32} 
        />
      </div>
      <div className="flex-grow-1 min-w-0">
        <div className="d-flex align-items-center mb-1">
          <span className="me-2" style={{ fontSize: '1.1em' }}>
            {getActivityIcon(activity.type)}
          </span>
          <span className={`fw-medium ${getActivityColor(activity.priority)}`}>
            {activity.user_name}
          </span>
          <small className="text-muted ms-2">
            {formatTimeAgo(activity.timestamp)}
          </small>
        </div>
        <p className="mb-0 text-dark small">
          {activity.message}
        </p>
        {activity.details && activity.details.event_title && (
          <small className="text-muted">
            📅 {activity.details.event_title}
          </small>
        )}
      </div>
    </div>
  );
};

export const ActivityFeed = ({ className = '', maxHeight = '400px' }) => {
  const [activities, setActivities] = useState([]);
  const [isVisible, setIsVisible] = useState(true);
  const activityEndRef = useRef(null);
  const { registerEventHandler } = useWebSocket();

  // Handle new member activities
  useEffect(() => {
    const handleMemberActivity = (data) => {
      console.log('New member activity received:', data);
      
      if (data.activity) {
        setActivities(prev => {
          // Check if activity already exists (prevent duplicates)
          const exists = prev.some(a => a.id === data.activity.id);
          if (exists) return prev;
          
          // Add new activity to the top
          const newActivities = [data.activity, ...prev];
          
          // Keep only last 100 activities to prevent memory issues
          return newActivities.slice(0, 100);
        });
      }
    };

    // Register the activity handler with WebSocket
    if (registerEventHandler) {
      registerEventHandler('member_activity', handleMemberActivity);
    }

    return () => {
      // Cleanup will be handled by WebSocket context
    };
  }, [registerEventHandler]);

  // Auto-scroll to bottom when new activities arrive
  useEffect(() => {
    if (activityEndRef.current && activities.length > 0) {
      // Only auto-scroll if user is near the bottom
      const container = activityEndRef.current.parentElement;
      if (container) {
        const isNearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 50;
        if (isNearBottom) {
          activityEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }
  }, [activities]);

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  const clearActivities = () => {
    setActivities([]);
  };

  return (
    <div className={`card ${className}`}>
      <div className="card-header d-flex justify-content-between align-items-center bg-light">
        <h6 className="mb-0 fw-bold">
          🎵 Live Activity Feed
          {activities.length > 0 && (
            <span className="badge bg-primary ms-2">{activities.length}</span>
          )}
        </h6>
        <div className="d-flex gap-1">
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={toggleVisibility}
            title={isVisible ? 'Hide feed' : 'Show feed'}
          >
            <i className={`bi bi-eye${isVisible ? '-slash' : ''}`}></i>
          </button>
          {activities.length > 0 && (
            <button
              className="btn btn-sm btn-outline-danger"
              onClick={clearActivities}
              title="Clear activities"
            >
              <i className="bi bi-trash"></i>
            </button>
          )}
        </div>
      </div>
      
      {isVisible && (
        <div 
          className="card-body p-3"
          style={{ 
            maxHeight: maxHeight, 
            overflowY: 'auto',
            backgroundColor: '#fafafa'
          }}
        >
          {activities.length === 0 ? (
            <div className="text-center text-muted py-4">
              <div style={{ fontSize: '2em' }}>🎵</div>
              <p className="mb-0">No recent activity</p>
              <small>Member actions will appear here in real-time</small>
            </div>
          ) : (
            <>
              {activities.map(activity => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
              <div ref={activityEndRef} />
            </>
          )}
        </div>
      )}
      
      {!isVisible && activities.length > 0 && (
        <div className="card-body p-2 text-center text-muted">
          <small>Activity feed hidden ({activities.length} activities)</small>
        </div>
      )}
    </div>
  );
};

export const CompactActivityFeed = () => {
  const [recentActivities, setRecentActivities] = useState([]);
  const { registerEventHandler } = useWebSocket();

  useEffect(() => {
    const handleMemberActivity = (data) => {
      if (data.activity) {
        setRecentActivities(prev => {
          const newActivities = [data.activity, ...prev];
          return newActivities.slice(0, 5); // Keep only 5 recent activities
        });
      }
    };

    if (registerEventHandler) {
      registerEventHandler('member_activity', handleMemberActivity);
    }
  }, [registerEventHandler]);

  if (recentActivities.length === 0) {
    return null;
  }

  return (
    <div className="alert alert-info d-flex align-items-center mb-3" role="alert">
      <div className="flex-grow-1">
        <strong>Recent Activity:</strong>
        <div className="small mt-1">
          {recentActivities[0].message}
          {recentActivities.length > 1 && (
            <span className="text-muted"> +{recentActivities.length - 1} more</span>
          )}
        </div>
      </div>
      <div className="flex-shrink-0">
        <i className="bi bi-broadcast text-primary" style={{ fontSize: '1.2em' }}></i>
      </div>
    </div>
  );
};

export default ActivityFeed;
