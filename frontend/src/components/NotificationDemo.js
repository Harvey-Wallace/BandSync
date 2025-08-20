import React, { useState } from 'react';
import { realTimeNotifications } from '../utils/realTimeNotifications';

const NotificationDemo = () => {
  const [demoRunning, setDemoRunning] = useState(false);

  const runNotificationDemo = async () => {
    if (demoRunning) return;
    
    setDemoRunning(true);
    
    // Demo sequence of different notification types
    const demoNotifications = [
      {
        title: '🎵 New Event Created',
        message: 'Jazz Night has been scheduled for Friday, August 25th',
        type: 'success',
        category: 'event',
        actions: [
          { action: 'view_event', title: 'View Event' },
          { action: 'rsvp_yes', title: 'RSVP Yes' }
        ]
      },
      {
        title: '📝 RSVP Update',
        message: 'Sarah Johnson changed their RSVP to "Yes" for Jazz Night',
        type: 'info',
        category: 'rsvp',
        actions: [
          { action: 'view_event', title: 'View Event' }
        ]
      },
      {
        title: '💬 New Message',
        message: 'John Smith: "Don\'t forget to bring your music stands!"',
        type: 'info',
        category: 'message',
        actions: [
          { action: 'view_message', title: 'Read Message' },
          { action: 'reply', title: 'Reply' }
        ]
      },
      {
        title: '⏰ Event Reminder',
        message: 'Jazz Night is starting in 30 minutes',
        type: 'warning',
        category: 'reminder',
        actions: [
          { action: 'view_event', title: 'View Event' },
          { action: 'confirm_attendance', title: 'Confirm' }
        ]
      },
      {
        title: '🔧 Admin Notice',
        message: 'Rehearsal room has been changed to Room B',
        type: 'warning',
        category: 'admin',
        actions: [
          { action: 'view_admin', title: 'View Details' }
        ]
      }
    ];

    // Show notifications with delays
    for (let i = 0; i < demoNotifications.length; i++) {
      setTimeout(() => {
        const notification = {
          ...demoNotifications[i],
          id: `demo-${Date.now()}-${i}`,
          timestamp: new Date(),
          data: { demo: true }
        };
        
        realTimeNotifications.showNotification(notification);
        
        if (i === demoNotifications.length - 1) {
          setTimeout(() => setDemoRunning(false), 1000);
        }
      }, i * 2000);
    }
  };

  const testDesktopNotification = async () => {
    const testNotif = {
      id: `desktop-test-${Date.now()}`,
      title: '🔔 Desktop Notification Test',
      message: 'This is a test of desktop notifications with actions!',
      type: 'success',
      category: 'test',
      timestamp: new Date(),
      actions: [
        { action: 'view_all', title: 'View App' },
        { action: 'close', title: 'Close' }
      ]
    };

    await realTimeNotifications.showDesktopNotification(testNotif);
  };

  const simulateWebSocketMessage = () => {
    // Simulate different types of WebSocket messages
    const messageTypes = [
      {
        type: 'rsvp_change',
        event_id: 123,
        user_id: 456,
        user_name: 'Demo User',
        event_title: 'Practice Session',
        old_status: 'Maybe',
        new_status: 'Yes'
      },
      {
        type: 'new_event',
        event_id: 789,
        event_title: 'Concert Rehearsal',
        event_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        type: 'new_message',
        thread_id: 101,
        message_id: 202,
        sender_id: 303,
        sender_name: 'Demo Sender',
        subject: 'Important Update',
        preview: 'Please check the latest schedule changes...',
        timestamp: new Date().toISOString()
      }
    ];

    const randomMessage = messageTypes[Math.floor(Math.random() * messageTypes.length)];
    realTimeNotifications.handleMessage(randomMessage);
  };

  const status = realTimeNotifications.getStatus();

  return (
    <div className="card card-enhanced mb-4">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="bi bi-bell-fill me-2"></i>
          Real-Time Notifications Demo
        </h5>
      </div>
      <div className="card-body">
        <div className="row mb-3">
          <div className="col-md-6">
            <h6>Connection Status</h6>
            <div className="d-flex align-items-center gap-2 mb-2">
              <span className={`badge ${status.connected ? 'bg-success' : 'bg-danger'}`}>
                {status.connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
              <small className="text-muted">
                Queue: {status.queuedNotifications || 0}
              </small>
            </div>
          </div>
          <div className="col-md-6">
            <h6>Notification Permission</h6>
            <span className={`badge ${
              typeof Notification !== 'undefined' && Notification.permission === 'granted' 
                ? 'bg-success' 
                : 'bg-warning'
            }`}>
              {typeof Notification !== 'undefined' 
                ? Notification.permission === 'granted' ? '✅ Granted' : '⚠️ ' + Notification.permission
                : '❌ Not Supported'
              }
            </span>
          </div>
        </div>

        <div className="d-flex gap-2 flex-wrap">
          <button 
            className="btn btn-primary touch-target mobile-button"
            onClick={runNotificationDemo}
            disabled={demoRunning}
            style={{ minHeight: '44px' }}
          >
            {demoRunning ? (
              <>
                <span className="spinner-border spinner-border-sm me-2"></span>
                Running Demo...
              </>
            ) : (
              <>
                <i className="bi bi-play-fill me-2"></i>
                Run Demo Sequence
              </>
            )}
          </button>

          <button 
            className="btn btn-outline-success touch-target mobile-button"
            onClick={testDesktopNotification}
            style={{ minHeight: '44px' }}
          >
            <i className="bi bi-desktop me-2"></i>
            Test Desktop
          </button>

          <button 
            className="btn btn-outline-info touch-target mobile-button"
            onClick={simulateWebSocketMessage}
            style={{ minHeight: '44px' }}
          >
            <i className="bi bi-wifi me-2"></i>
            Simulate Message
          </button>

          <button 
            className="btn btn-outline-warning touch-target mobile-button"
            onClick={() => {
              if (window.showSuccess) window.showSuccess('🎵 Simple test notification!');
            }}
            style={{ minHeight: '44px' }}
          >
            <i className="bi bi-check-circle me-2"></i>
            Simple Test
          </button>
        </div>

        <div className="mt-3">
          <small className="text-muted">
            <strong>Demo Features:</strong> This demo shows real-time notifications with different categories, 
            action buttons, desktop notifications, and WebSocket message simulation. 
            The notification system includes smart batching, sound effects, and mobile optimization.
          </small>
        </div>
      </div>
    </div>
  );
};

export default NotificationDemo;
