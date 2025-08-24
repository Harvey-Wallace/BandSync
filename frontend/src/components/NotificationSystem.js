import React, { useState, useEffect } from 'react';
import { realTimeNotifications } from '../utils/realTimeNotifications';
import NotificationPreferences from './NotificationPreferences';

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([]);
  const [showPreferences, setShowPreferences] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState({ connected: false });

  // Enhanced notification structure
  const addNotification = (message, type = 'info', duration = 5000, options = {}) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type,
      timestamp: new Date(),
      duration,
      title: options.title,
      category: options.category || 'general',
      actions: options.actions || [],
      data: options.data || {},
      persistent: options.persistent || false
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-remove notification after duration (unless persistent)
    if (duration > 0 && !notification.persistent) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  };

  // Function to remove a notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  // Handle notification actions
  const handleNotificationAction = (notification, action) => {
    switch (action.action) {
      case 'view_event':
        if (notification.data?.eventId) {
          window.location.href = `/events#event-${notification.data.eventId}`;
        }
        break;
      case 'view_message':
        if (notification.data?.threadId) {
          window.location.href = `/messaging#thread-${notification.data.threadId}`;
        }
        break;
      case 'view_admin':
        window.location.href = '/admin';
        break;
      case 'rsvp_yes':
        if (notification.data?.eventId) {
          // Could integrate with RSVP system here
          window.showSuccess('RSVP feature coming soon!');
        }
        break;
      case 'view_all':
        setShowPreferences(true);
        break;
      default:
        console.log('Unknown action:', action);
    }
    
    // Remove notification after action unless persistent
    if (!notification.persistent) {
      removeNotification(notification.id);
    }
  };

  // Global notification functions
  useEffect(() => {
    // Attach notification functions to window for global access
    window.showNotification = addNotification;
    window.hideNotification = removeNotification;

    // Enhanced convenience functions with better defaults
    window.showSuccess = (message, duration = 4000, options = {}) => 
      addNotification(message, 'success', duration, { ...options, title: options.title || 'Success' });
    window.showError = (message, duration = 8000, options = {}) => 
      addNotification(message, 'error', duration, { ...options, title: options.title || 'Error', persistent: true });
    window.showWarning = (message, duration = 6000, options = {}) => 
      addNotification(message, 'warning', duration, { ...options, title: options.title || 'Warning' });
    window.showInfo = (message, duration = 5000, options = {}) => 
      addNotification(message, 'info', duration, { ...options, title: options.title || 'Info' });

    // Listen to real-time notifications
    const handleRealTimeNotification = (notification) => {
      addNotification(
        notification.message, 
        notification.type, 
        notification.persistent ? 0 : 5000,
        {
          title: notification.title,
          category: notification.category,
          actions: notification.actions,
          data: notification.data,
          persistent: notification.persistent
        }
      );
    };

    const handleConnectionChange = () => {
      const status = realTimeNotifications.getStatus();
      setConnectionStatus(status);
    };

    const handleConnectionFailed = () => {
      // Don't show persistent warnings for connection failures
      // This typically happens in development when no WebSocket server is available
      console.log('Real-time notifications connection failed - operating in fallback mode');
      setConnectionStatus({ connected: false, connectionFailed: true });
    };

    realTimeNotifications.on('notification', handleRealTimeNotification);
    realTimeNotifications.on('connected', handleConnectionChange);
    realTimeNotifications.on('disconnected', handleConnectionChange);
    realTimeNotifications.on('connectionFailed', handleConnectionFailed);

    // Initial status load
    handleConnectionChange();

    return () => {
      // Cleanup
      delete window.showNotification;
      delete window.hideNotification;
      delete window.showSuccess;
      delete window.showError;
      delete window.showWarning;
      delete window.showInfo;
      
      realTimeNotifications.off('notification', handleRealTimeNotification);
      realTimeNotifications.off('connected', handleConnectionChange);
      realTimeNotifications.off('disconnected', handleConnectionChange);
      realTimeNotifications.off('connectionFailed', handleConnectionFailed);
    };
  }, []);

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <i className="bi bi-check-circle-fill me-2"></i>;
      case 'error':
        return <i className="bi bi-exclamation-triangle-fill me-2"></i>;
      case 'warning':
        return <i className="bi bi-exclamation-circle-fill me-2"></i>;
      case 'info':
      default:
        return <i className="bi bi-info-circle-fill me-2"></i>;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'rsvp':
        return <i className="bi bi-person-check text-info me-2"></i>;
      case 'event':
        return <i className="bi bi-calendar-event text-success me-2"></i>;
      case 'message':
        return <i className="bi bi-chat-dots text-primary me-2"></i>;
      case 'reminder':
        return <i className="bi bi-alarm text-warning me-2"></i>;
      case 'admin':
        return <i className="bi bi-shield-check text-danger me-2"></i>;
      case 'summary':
        return <i className="bi bi-collection text-info me-2"></i>;
      default:
        return null;
    }
  };

  return (
    <>
      {/* Connection Status Indicator */}
      {!connectionStatus.connected && !connectionStatus.connectionFailed && (
        <div className="position-fixed top-0 end-0 p-3" style={{ zIndex: 1060 }}>
          <div className="alert alert-warning d-flex align-items-center mb-0 shadow-sm" role="alert">
            <i className="bi bi-wifi-off me-2"></i>
            <small>Real-time notifications disconnected</small>
            <button 
              className="btn btn-sm btn-outline-secondary ms-2"
              onClick={() => setShowPreferences(true)}
              style={{ fontSize: '0.75rem' }}
            >
              Settings
            </button>
          </div>
        </div>
      )}

      {/* Notification Container */}
      <div className="notification-container">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`notification notification-${notification.type} notification-enhanced fade-in ${
              notification.actions && notification.actions.length > 0 ? 'notification-with-actions' : ''
            }`}
          >
            <div className="notification-content">
              {/* Header */}
              <div className="d-flex align-items-start justify-content-between">
                <div className="d-flex align-items-start flex-grow-1">
                  <div className="flex-shrink-0 d-flex align-items-center">
                    {getCategoryIcon(notification.category)}
                    {getIcon(notification.type)}
                  </div>
                  <div className="flex-grow-1">
                    {notification.title && (
                      <div className="notification-title fw-bold mb-1">
                        {typeof notification.title === 'string' ? notification.title : 'Notification'}
                      </div>
                    )}
                    <div className="notification-message">
                      {typeof notification.message === 'string' ? notification.message : 'New notification'}
                    </div>
                    <small className="text-muted d-block mt-1">
                      {notification.timestamp.toLocaleTimeString()}
                      {notification.category && notification.category !== 'general' && (
                        <> • {typeof notification.category === 'string' ? notification.category : 'notification'}</>
                      )}
                    </small>
                  </div>
                </div>
                
                {!notification.persistent && (
                  <button
                    className="notification-close touch-target"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeNotification(notification.id);
                    }}
                    aria-label="Close notification"
                    style={{ minHeight: '32px', minWidth: '32px' }}
                  >
                    <i className="bi bi-x"></i>
                  </button>
                )}
              </div>

              {/* Actions */}
              {notification.actions && notification.actions.length > 0 && (
                <div className="notification-actions mt-2 pt-2 border-top">
                  <div className="d-flex gap-2 flex-wrap">
                    {notification.actions.slice(0, 3).map((action, index) => (
                      <button
                        key={index}
                        className="btn btn-sm btn-outline-light touch-target mobile-button"
                        onClick={() => handleNotificationAction(notification, action)}
                        style={{ minHeight: '32px' }}
                      >
                        {typeof action.title === 'string' ? action.title : `Action ${index + 1}`}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Floating Notification Settings Button */}
      {connectionStatus.connected && (
        <div className="position-fixed bottom-0 end-0 p-3" style={{ zIndex: 1050 }}>
          <button
            className="btn btn-primary btn-sm rounded-circle shadow-lg touch-target"
            onClick={() => setShowPreferences(true)}
            title="Notification Settings"
            style={{ width: '48px', height: '48px' }}
          >
            <i className="bi bi-bell-fill"></i>
          </button>
        </div>
      )}

      {/* Notification Preferences Modal */}
      <NotificationPreferences 
        showModal={showPreferences}
        onClose={() => setShowPreferences(false)}
      />
    </>
  );
};

export default NotificationSystem;
