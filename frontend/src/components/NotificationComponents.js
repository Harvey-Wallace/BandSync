/**
 * Real-time Notification Component
 * Displays live notifications with toast-style notifications and notification center
 */

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';

// Individual notification toast component
const NotificationToast = ({ notification, onClose, onMarkRead }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Auto-hide after 5 seconds
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose(notification.id), 300); // Wait for fade out
    }, 5000);

    return () => clearTimeout(timer);
  }, [notification.id, onClose]);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'rsvp':
        return '✅';
      case 'event':
        return '📅';
      case 'info':
        return 'ℹ️';
      default:
        return '🔔';
    }
  };

  const getNotificationClass = (type) => {
    switch (type) {
      case 'rsvp':
        return 'alert-success';
      case 'event':
        return 'alert-primary';
      case 'info':
        return 'alert-info';
      default:
        return 'alert-secondary';
    }
  };

  const handleClick = () => {
    if (!notification.read) {
      onMarkRead(notification.id);
    }
  };

  return (
    <div 
      className={`alert ${getNotificationClass(notification.type)} alert-dismissible fade ${isVisible ? 'show' : ''} mb-2`}
      style={{
        transition: 'all 0.3s ease',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
        cursor: 'pointer',
        maxWidth: '400px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}
      onClick={handleClick}
      role="alert"
    >
      <div className="d-flex align-items-start">
        <span className="me-2" style={{ fontSize: '1.2em' }}>
          {getNotificationIcon(notification.type)}
        </span>
        <div className="flex-grow-1">
          <div className="fw-bold small">
            {notification.message}
          </div>
          {notification.data && notification.data.event_title && (
            <div className="small text-muted">
              Event: {notification.data.event_title}
            </div>
          )}
          <div className="small text-muted">
            {new Date(notification.timestamp).toLocaleTimeString()}
          </div>
        </div>
        <button
          type="button"
          className="btn-close btn-close-sm"
          onClick={(e) => {
            e.stopPropagation();
            setIsVisible(false);
            setTimeout(() => onClose(notification.id), 300);
          }}
          aria-label="Close"
        ></button>
      </div>
    </div>
  );
};

// Floating notification container
export const NotificationToastContainer = () => {
  const { notifications } = useWebSocket();
  const [visibleNotifications, setVisibleNotifications] = useState([]);

  useEffect(() => {
    // Show only the last 3 notifications as toasts
    const recentNotifications = notifications.slice(0, 3);
    setVisibleNotifications(recentNotifications);
  }, [notifications]);

  const removeNotification = (notificationId) => {
    setVisibleNotifications(prev => 
      prev.filter(notif => notif.id !== notificationId)
    );
  };

  const { markNotificationAsRead } = useWebSocket();

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 1055,
        pointerEvents: 'none'
      }}
    >
      <div style={{ pointerEvents: 'auto' }}>
        {visibleNotifications.map(notification => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onClose={removeNotification}
            onMarkRead={markNotificationAsRead}
          />
        ))}
      </div>
    </div>
  );
};

// Notification center component
export const NotificationCenter = ({ isOpen, onClose }) => {
  const { 
    notifications, 
    unreadCount, 
    markNotificationAsRead, 
    clearNotifications,
    isConnected,
    connectionStatus
  } = useWebSocket();

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      markNotificationAsRead(notification.id);
    }
  };

  const getConnectionStatusBadge = () => {
    switch (connectionStatus) {
      case 'connected':
        return <span className="badge bg-success">Connected</span>;
      case 'connecting':
        return <span className="badge bg-warning">Connecting...</span>;
      case 'error':
        return <span className="badge bg-danger">Error</span>;
      default:
        return <span className="badge bg-secondary">Disconnected</span>;
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="position-fixed top-0 end-0 bg-white border shadow-lg"
      style={{
        width: '400px',
        height: '500px',
        zIndex: 1060,
        marginTop: '60px',
        marginRight: '20px',
        borderRadius: '8px',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <div className="bg-primary text-white p-3 d-flex justify-content-between align-items-center">
        <div>
          <h6 className="mb-0">🔔 Notifications</h6>
          <small>
            {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
          </small>
        </div>
        <div className="d-flex align-items-center gap-2">
          {getConnectionStatusBadge()}
          <button
            type="button"
            className="btn-close btn-close-white"
            onClick={onClose}
            aria-label="Close"
          ></button>
        </div>
      </div>

      {/* Connection Status */}
      <div className="p-2 bg-light border-bottom">
        <div className="d-flex align-items-center justify-content-between">
          <small className="text-muted">
            Real-time updates: {isConnected ? '✅ Active' : '❌ Inactive'}
          </small>
          {notifications.length > 0 && (
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={clearNotifications}
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <div 
        className="overflow-auto"
        style={{ height: 'calc(100% - 120px)' }}
      >
        {notifications.length === 0 ? (
          <div className="text-center p-4 text-muted">
            <div style={{ fontSize: '3em' }}>🔔</div>
            <p>No notifications yet</p>
            <small>Real-time updates will appear here</small>
          </div>
        ) : (
          <div className="p-2">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`card mb-2 ${notification.read ? 'border-light' : 'border-primary'}`}
                style={{ 
                  cursor: 'pointer',
                  backgroundColor: notification.read ? '#f8f9fa' : '#fff'
                }}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="card-body p-3">
                  <div className="d-flex align-items-start">
                    <span className="me-2" style={{ fontSize: '1.1em' }}>
                      {notification.type === 'rsvp' ? '✅' : 
                       notification.type === 'event' ? '📅' : '🔔'}
                    </span>
                    <div className="flex-grow-1">
                      <div className={`small ${notification.read ? 'text-muted' : 'text-dark fw-bold'}`}>
                        {notification.message}
                      </div>
                      {notification.data && notification.data.event_title && (
                        <div className="small text-muted mt-1">
                          Event: {notification.data.event_title}
                        </div>
                      )}
                      <div className="small text-muted mt-1">
                        {new Date(notification.timestamp).toLocaleString()}
                      </div>
                    </div>
                    {!notification.read && (
                      <span className="badge bg-primary rounded-pill">New</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Notification bell icon component
export const NotificationBell = ({ onClick }) => {
  const { unreadCount, isConnected, requestNotificationPermission } = useWebSocket();

  useEffect(() => {
    // Request notification permission on component mount
    requestNotificationPermission();
  }, [requestNotificationPermission]);

  return (
    <button
      className="btn btn-outline-light position-relative me-2"
      onClick={onClick}
      title="Notifications"
      style={{
        border: 'none',
        background: 'transparent'
      }}
    >
      <span style={{ fontSize: '1.2em' }}>
        {isConnected ? '🔔' : '🔕'}
      </span>
      {unreadCount > 0 && (
        <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
          {unreadCount > 99 ? '99+' : unreadCount}
          <span className="visually-hidden">unread notifications</span>
        </span>
      )}
    </button>
  );
};
