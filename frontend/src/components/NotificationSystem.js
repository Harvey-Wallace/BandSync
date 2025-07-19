import React, { useState, useEffect } from 'react';

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([]);

  // Function to add a notification
  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type,
      timestamp: new Date()
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-remove notification after duration
    if (duration > 0) {
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

  // Global notification functions
  useEffect(() => {
    // Attach notification functions to window for global access
    window.showNotification = addNotification;
    window.hideNotification = removeNotification;

    // Convenience functions for different notification types
    window.showSuccess = (message, duration = 4000) => addNotification(message, 'success', duration);
    window.showError = (message, duration = 6000) => addNotification(message, 'error', duration);
    window.showWarning = (message, duration = 5000) => addNotification(message, 'warning', duration);
    window.showInfo = (message, duration = 5000) => addNotification(message, 'info', duration);

    return () => {
      // Cleanup
      delete window.showNotification;
      delete window.hideNotification;
      delete window.showSuccess;
      delete window.showError;
      delete window.showWarning;
      delete window.showInfo;
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

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification-${notification.type} fade-in`}
          onClick={() => removeNotification(notification.id)}
        >
          <div className="d-flex align-items-start">
            <div className="flex-shrink-0">
              {getIcon(notification.type)}
            </div>
            <div className="flex-grow-1">
              <div className="notification-message">
                {notification.message}
              </div>
              <small className="text-muted">
                {notification.timestamp.toLocaleTimeString()}
              </small>
            </div>
            <button
              className="notification-close"
              onClick={(e) => {
                e.stopPropagation();
                removeNotification(notification.id);
              }}
              aria-label="Close notification"
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationSystem;
