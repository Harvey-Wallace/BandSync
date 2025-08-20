import React, { useState, useEffect } from 'react';
import { realTimeNotifications } from '../utils/realTimeNotifications';

const NotificationPreferences = ({ showModal, onClose }) => {
  const [preferences, setPreferences] = useState({});
  const [status, setStatus] = useState({});
  const [testNotification, setTestNotification] = useState(false);

  useEffect(() => {
    // Load initial preferences and status
    loadPreferences();
    loadStatus();

    // Listen for preference updates
    const handlePreferencesUpdate = (newPreferences) => {
      setPreferences(newPreferences);
    };

    const handleStatusUpdate = () => {
      loadStatus();
    };

    realTimeNotifications.on('preferencesUpdated', handlePreferencesUpdate);
    realTimeNotifications.on('connected', handleStatusUpdate);
    realTimeNotifications.on('disconnected', handleStatusUpdate);

    return () => {
      realTimeNotifications.off('preferencesUpdated', handlePreferencesUpdate);
      realTimeNotifications.off('connected', handleStatusUpdate);
      realTimeNotifications.off('disconnected', handleStatusUpdate);
    };
  }, []);

  const loadPreferences = () => {
    const currentPrefs = realTimeNotifications.loadPreferences();
    setPreferences(currentPrefs);
  };

  const loadStatus = () => {
    const currentStatus = realTimeNotifications.getStatus();
    setStatus(currentStatus);
  };

  const handlePreferenceChange = (key, value) => {
    const updatedPreferences = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPreferences);
    realTimeNotifications.updatePreferences(updatedPreferences);
  };

  const handleTestNotification = async () => {
    setTestNotification(true);
    
    // Test in-app notification
    if (window.showSuccess) {
      window.showSuccess('🎵 Test notification working perfectly!', 3000);
    }

    // Test desktop notification
    const testNotif = {
      id: `test-${Date.now()}`,
      title: '🔔 BandSync Test Notification',
      message: 'Your notifications are working perfectly!',
      type: 'success',
      category: 'test',
      timestamp: new Date(),
      actions: []
    };

    await realTimeNotifications.showDesktopNotification(testNotif);
    
    // Test sound if enabled
    if (preferences.sound) {
      realTimeNotifications.playNotificationSound('success');
    }

    setTimeout(() => setTestNotification(false), 2000);
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      loadStatus(); // Refresh status after permission change
      
      if (permission === 'granted') {
        if (window.showSuccess) {
          window.showSuccess('🔔 Desktop notifications enabled!');
        }
      } else {
        if (window.showWarning) {
          window.showWarning('Desktop notifications were denied. You can enable them in your browser settings.');
        }
      }
    }
  };

  const getConnectionStatusBadge = () => {
    if (status.connected) {
      return <span className="badge bg-success">🟢 Connected</span>;
    } else {
      return <span className="badge bg-danger">🔴 Disconnected</span>;
    }
  };

  const getNotificationPermissionStatus = () => {
    if (!('Notification' in window)) {
      return <span className="badge bg-secondary">Not Supported</span>;
    }
    
    switch (Notification.permission) {
      case 'granted':
        return <span className="badge bg-success">✅ Enabled</span>;
      case 'denied':
        return <span className="badge bg-danger">❌ Blocked</span>;
      default:
        return <span className="badge bg-warning">⚠️ Not Set</span>;
    }
  };

  if (!showModal) return null;

  return (
    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content card-enhanced">
          <div className="modal-header bg-gradient-primary text-white">
            <h5 className="modal-title">
              <i className="bi bi-bell me-2"></i>
              Notification Settings
            </h5>
            <button 
              type="button" 
              className="btn-close btn-close-white" 
              onClick={onClose}
            ></button>
          </div>
          
          <div className="modal-body">
            {/* Connection Status */}
            <div className="card mb-4">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="bi bi-wifi me-2"></i>
                  Connection Status
                </h6>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Real-Time Connection:</strong>{' '}
                      {getConnectionStatusBadge()}
                    </div>
                    <div className="mb-3">
                      <strong>Desktop Notifications:</strong>{' '}
                      {getNotificationPermissionStatus()}
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <strong>Queued Notifications:</strong>{' '}
                      <span className="badge bg-info">{status.queuedNotifications || 0}</span>
                    </div>
                    {status.reconnectAttempts > 0 && (
                      <div className="mb-3">
                        <strong>Reconnect Attempts:</strong>{' '}
                        <span className="badge bg-warning">{status.reconnectAttempts}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-outline-primary btn-sm touch-target mobile-button"
                    onClick={handleTestNotification}
                    disabled={testNotification}
                    style={{ minHeight: '40px' }}
                  >
                    {testNotification ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Testing...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-bell-fill me-2"></i>
                        Test Notifications
                      </>
                    )}
                  </button>
                  
                  {Notification?.permission !== 'granted' && 'Notification' in window && (
                    <button 
                      className="btn btn-outline-success btn-sm touch-target mobile-button"
                      onClick={requestNotificationPermission}
                      style={{ minHeight: '40px' }}
                    >
                      <i className="bi bi-check-circle me-2"></i>
                      Enable Desktop
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Main Notification Preferences */}
            <div className="card mb-4">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="bi bi-gear me-2"></i>
                  Notification Preferences
                </h6>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6">
                    {/* Main Toggle */}
                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="notificationsEnabled"
                        checked={preferences.enabled || false}
                        onChange={(e) => handlePreferenceChange('enabled', e.target.checked)}
                      />
                      <label className="form-check-label fw-bold" htmlFor="notificationsEnabled">
                        <i className="bi bi-bell-fill me-2 text-primary"></i>
                        Enable All Notifications
                      </label>
                    </div>

                    {/* Desktop Notifications */}
                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="showOnDesktop"
                        checked={preferences.showOnDesktop || false}
                        onChange={(e) => handlePreferenceChange('showOnDesktop', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="showOnDesktop">
                        <i className="bi bi-display me-2 text-info"></i>
                        Desktop Notifications
                      </label>
                    </div>

                    {/* Sound */}
                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="sound"
                        checked={preferences.sound || false}
                        onChange={(e) => handlePreferenceChange('sound', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="sound">
                        <i className="bi bi-volume-up me-2 text-warning"></i>
                        Notification Sounds
                      </label>
                    </div>

                    {/* Vibration */}
                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="vibration"
                        checked={preferences.vibration || false}
                        onChange={(e) => handlePreferenceChange('vibration', e.target.checked)}
                        disabled={!preferences.enabled || !('vibrate' in navigator)}
                      />
                      <label className="form-check-label" htmlFor="vibration">
                        <i className="bi bi-phone-vibrate me-2 text-success"></i>
                        Vibration {!('vibrate' in navigator) && '(Not Supported)'}
                      </label>
                    </div>
                  </div>

                  <div className="col-md-6">
                    {/* Notification Categories */}
                    <h6 className="mb-3 text-muted">Notification Categories</h6>
                    
                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="newEvents"
                        checked={preferences.newEvents || false}
                        onChange={(e) => handlePreferenceChange('newEvents', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="newEvents">
                        <i className="bi bi-calendar-plus me-2 text-success"></i>
                        New Events
                      </label>
                    </div>

                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="rsvpChanges"
                        checked={preferences.rsvpChanges || false}
                        onChange={(e) => handlePreferenceChange('rsvpChanges', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="rsvpChanges">
                        <i className="bi bi-person-check me-2 text-info"></i>
                        RSVP Changes
                      </label>
                    </div>

                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="messages"
                        checked={preferences.messages || false}
                        onChange={(e) => handlePreferenceChange('messages', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="messages">
                        <i className="bi bi-chat-dots me-2 text-primary"></i>
                        Messages
                      </label>
                    </div>

                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="eventReminders"
                        checked={preferences.eventReminders || false}
                        onChange={(e) => handlePreferenceChange('eventReminders', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="eventReminders">
                        <i className="bi bi-alarm me-2 text-warning"></i>
                        Event Reminders
                      </label>
                    </div>

                    <div className="form-check form-switch mb-3">
                      <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="adminNotifications"
                        checked={preferences.adminNotifications || false}
                        onChange={(e) => handlePreferenceChange('adminNotifications', e.target.checked)}
                        disabled={!preferences.enabled}
                      />
                      <label className="form-check-label" htmlFor="adminNotifications">
                        <i className="bi bi-shield-check me-2 text-danger"></i>
                        Admin Notifications
                      </label>
                    </div>
                  </div>
                </div>

                {/* Batch Delay */}
                <div className="mt-4">
                  <label htmlFor="batchDelay" className="form-label">
                    <i className="bi bi-clock me-2"></i>
                    Notification Batching Delay: <strong>{preferences.batchDelay || 2000}ms</strong>
                  </label>
                  <input 
                    type="range" 
                    className="form-range" 
                    id="batchDelay"
                    min="0" 
                    max="10000" 
                    step="500"
                    value={preferences.batchDelay || 2000}
                    onChange={(e) => handlePreferenceChange('batchDelay', parseInt(e.target.value))}
                    disabled={!preferences.enabled}
                  />
                  <div className="d-flex justify-content-between">
                    <small className="text-muted">Instant (0ms)</small>
                    <small className="text-muted">10 seconds</small>
                  </div>
                  <small className="text-muted">
                    When you're not viewing the tab, notifications will be batched and shown together after this delay.
                  </small>
                </div>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="card">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="bi bi-gear-fill me-2"></i>
                  Advanced Settings
                </h6>
              </div>
              <div className="card-body">
                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  <strong>Smart Batching:</strong> When you're not viewing the BandSync tab, 
                  notifications are intelligently batched to avoid overwhelming you. When you return 
                  to the tab, you'll see a summary of what happened while you were away.
                </div>
                
                <div className="alert alert-warning">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  <strong>Battery Optimization:</strong> Real-time notifications use WebSocket 
                  connections which may affect battery life on mobile devices. You can disable 
                  real-time features if battery life is a concern.
                </div>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-secondary touch-target mobile-button" 
              onClick={onClose}
              style={{ minHeight: '44px' }}
            >
              <i className="bi bi-x-circle me-2"></i>
              Close
            </button>
            <button 
              type="button" 
              className="btn btn-primary touch-target mobile-button" 
              onClick={() => {
                if (window.showSuccess) {
                  window.showSuccess('🔔 Notification preferences saved!');
                }
                onClose();
              }}
              style={{ minHeight: '44px' }}
            >
              <i className="bi bi-check-circle me-2"></i>
              Save & Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationPreferences;
