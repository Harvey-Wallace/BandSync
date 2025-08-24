// Real-Time Notification Manager
// Handles WebSocket connections, push notifications, and real-time updates

class RealTimeNotificationManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3; // Reduced from 5
    this.reconnectDelay = 1000;
    this.heartbeatInterval = null;
    this.isConnected = false;
    this.connectionFailed = false; // Track if connection consistently fails
    this.listeners = new Map();
    this.notificationQueue = [];
    this.isVisible = !document.hidden;
    
    // Notification preferences
    this.preferences = this.loadPreferences();
    
    // Initialize visibility tracking
    this.initializeVisibilityTracking();
    
    // Only auto-connect if WebSocket is likely supported and we have a token
    if (this.shouldAttemptConnection()) {
      // Delay initial connection to avoid blocking UI
      setTimeout(() => this.connect(), 2000);
    } else {
      this.connectionFailed = true;
    }
  }

  // Check if we should attempt WebSocket connection
  shouldAttemptConnection() {
    // Check if WebSocket is supported
    if (typeof WebSocket === 'undefined') {
      console.log('WebSocket not supported, skipping real-time notifications');
      return false;
    }

    // Check if we have authentication
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No auth token, skipping real-time notifications');
      return false;
    }

    // Disable WebSocket connections entirely until WebSocket server is implemented
    console.log('WebSocket server not yet implemented, disabling real-time notifications');
    return false;

    // Check if we're in development and likely don't have a WebSocket server
    if (window.location.hostname === 'localhost' && !window.location.search.includes('ws=true')) {
      console.log('Development mode detected, real-time notifications disabled (add ?ws=true to enable)');
      return false;
    }

    return true;
  }

  // Load notification preferences from localStorage
  loadPreferences() {
    try {
      const saved = localStorage.getItem('notification_preferences');
      return saved ? JSON.parse(saved) : {
        enabled: true,
        sound: true,
        vibration: true,
        showOnDesktop: true,
        rsvpChanges: true,
        newEvents: true,
        messages: true,
        eventReminders: true,
        adminNotifications: true,
        batchDelay: 2000 // 2 second batching delay
      };
    } catch (error) {
      console.warn('Failed to load notification preferences:', error);
      return {
        enabled: true,
        sound: true,
        vibration: true,
        showOnDesktop: true,
        rsvpChanges: true,
        newEvents: true,
        messages: true,
        eventReminders: true,
        adminNotifications: true,
        batchDelay: 2000
      };
    }
  }

  // Save notification preferences
  savePreferences(preferences) {
    try {
      this.preferences = { ...this.preferences, ...preferences };
      localStorage.setItem('notification_preferences', JSON.stringify(this.preferences));
      this.emit('preferencesUpdated', this.preferences);
    } catch (error) {
      console.error('Failed to save notification preferences:', error);
    }
  }

  // Initialize visibility tracking for tab focus
  initializeVisibilityTracking() {
    document.addEventListener('visibilitychange', () => {
      this.isVisible = !document.hidden;
      
      if (this.isVisible) {
        // Clear any queued notifications when tab becomes visible
        this.processNotificationQueue();
      }
    });
  }

  // Connect to WebSocket
  connect() {
    // Don't attempt connection if we already determined it should fail
    if (this.connectionFailed || !this.shouldAttemptConnection()) {
      return;
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.warn('No auth token available for WebSocket connection');
        this.connectionFailed = true;
        return;
      }

      // Use secure WebSocket in production
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws?token=${encodeURIComponent(token)}`;

      console.log('Attempting WebSocket connection:', wsUrl);
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.emit('connected');
        
        // Request initial notification sync
        this.send({
          type: 'sync_notifications',
          timestamp: Date.now()
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        this.isConnected = false;
        this.stopHeartbeat();
        this.emit('disconnected');
        
        // Mark as failed if we've reached max attempts
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.log('Max reconnection attempts reached, disabling WebSocket');
          this.connectionFailed = true;
          this.emit('connectionFailed');
          return;
        }
        
        // Attempt to reconnect unless it was a clean close
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else if (event.code !== 1000) {
          this.connectionFailed = true;
          this.emit('connectionFailed');
        }
      };

      this.ws.onerror = (error) => {
        console.warn('WebSocket connection failed (likely no server available)');
        this.connectionFailed = true;
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  // Schedule reconnection attempt
  scheduleReconnect() {
    // Don't schedule reconnection if we shouldn't attempt connections
    if (!this.shouldAttemptConnection()) {
      console.log('Skipping reconnection - connection not advisable');
      this.connectionFailed = true;
      this.emit('connectionFailed');
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.connectionFailed = true;
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  // Start heartbeat to keep connection alive
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, 30000); // 30 second heartbeat
  }

  // Stop heartbeat
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // Send message through WebSocket
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data));
        return true;
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        return false;
      }
    } else {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }
  }

  // Handle incoming WebSocket messages
  handleMessage(data) {
    console.log('📡 Received WebSocket message:', data);

    switch (data.type) {
      case 'pong':
        // Heartbeat response
        break;
        
      case 'notification':
        this.handleNotification(data);
        break;
        
      case 'rsvp_change':
        this.handleRsvpChange(data);
        break;
        
      case 'new_event':
        this.handleNewEvent(data);
        break;
        
      case 'event_update':
        this.handleEventUpdate(data);
        break;
        
      case 'new_message':
        this.handleNewMessage(data);
        break;
        
      case 'event_reminder':
        this.handleEventReminder(data);
        break;
        
      case 'admin_notification':
        this.handleAdminNotification(data);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
        this.emit('message', data);
    }
  }

  // Handle generic notifications
  handleNotification(data) {
    if (!this.preferences.enabled) return;

    const notification = {
      id: data.id || Date.now(),
      title: data.title || 'BandSync Notification',
      message: data.message,
      type: data.notification_type || 'info',
      category: data.category || 'general',
      timestamp: new Date(data.timestamp || Date.now()),
      data: data.data || {},
      actions: data.actions || []
    };

    this.processNotification(notification);
  }

  // Handle RSVP changes
  handleRsvpChange(data) {
    if (!this.preferences.rsvpChanges) return;

    const notification = {
      id: `rsvp-${data.event_id}-${data.user_id}-${Date.now()}`,
      title: '🎵 RSVP Update',
      message: `${data.user_name} changed their RSVP for "${data.event_title}" to ${data.new_status}`,
      type: 'info',
      category: 'rsvp',
      timestamp: new Date(),
      data: {
        eventId: data.event_id,
        userId: data.user_id,
        oldStatus: data.old_status,
        newStatus: data.new_status
      },
      actions: [
        { action: 'view_event', title: 'View Event' }
      ]
    };

    this.processNotification(notification);
    this.emit('rsvpChange', data);
  }

  // Handle new events
  handleNewEvent(data) {
    if (!this.preferences.newEvents) return;

    const notification = {
      id: `event-${data.event_id}-${Date.now()}`,
      title: '📅 New Event Created',
      message: `"${data.event_title}" has been scheduled for ${new Date(data.event_date).toLocaleDateString()}`,
      type: 'success',
      category: 'event',
      timestamp: new Date(),
      data: {
        eventId: data.event_id,
        eventDate: data.event_date
      },
      actions: [
        { action: 'view_event', title: 'View Event' },
        { action: 'rsvp_yes', title: 'RSVP Yes' }
      ]
    };

    this.processNotification(notification);
    this.emit('newEvent', data);
  }

  // Handle event updates
  handleEventUpdate(data) {
    const notification = {
      id: `event-update-${data.event_id}-${Date.now()}`,
      title: '✏️ Event Updated',
      message: `"${data.event_title}" has been updated. ${data.changes_summary}`,
      type: 'warning',
      category: 'event',
      timestamp: new Date(),
      data: {
        eventId: data.event_id,
        changes: data.changes
      },
      actions: [
        { action: 'view_event', title: 'View Changes' }
      ]
    };

    this.processNotification(notification);
    this.emit('eventUpdate', data);
  }

  // Handle new messages
  handleNewMessage(data) {
    if (!this.preferences.messages) return;

    const notification = {
      id: `message-${data.thread_id}-${data.message_id}`,
      title: `💬 New Message from ${data.sender_name}`,
      message: data.subject || data.preview || 'New message received',
      type: 'info',
      category: 'message',
      timestamp: new Date(data.timestamp),
      data: {
        threadId: data.thread_id,
        messageId: data.message_id,
        senderId: data.sender_id
      },
      actions: [
        { action: 'view_message', title: 'Read Message' },
        { action: 'reply', title: 'Reply' }
      ]
    };

    this.processNotification(notification);
    this.emit('newMessage', data);
  }

  // Handle event reminders
  handleEventReminder(data) {
    if (!this.preferences.eventReminders) return;

    const notification = {
      id: `reminder-${data.event_id}-${Date.now()}`,
      title: `⏰ Event Reminder`,
      message: `"${data.event_title}" is coming up ${data.time_until}`,
      type: 'warning',
      category: 'reminder',
      timestamp: new Date(),
      data: {
        eventId: data.event_id,
        eventDate: data.event_date
      },
      actions: [
        { action: 'view_event', title: 'View Event' },
        { action: 'confirm_attendance', title: 'Confirm' }
      ]
    };

    this.processNotification(notification);
    this.emit('eventReminder', data);
  }

  // Handle admin notifications
  handleAdminNotification(data) {
    if (!this.preferences.adminNotifications) return;

    const notification = {
      id: `admin-${data.notification_id || Date.now()}`,
      title: `🔧 Admin: ${data.title}`,
      message: data.message,
      type: data.severity || 'info',
      category: 'admin',
      timestamp: new Date(data.timestamp),
      data: data.data || {},
      actions: data.actions || [
        { action: 'view_admin', title: 'View Admin Panel' }
      ]
    };

    this.processNotification(notification);
    this.emit('adminNotification', data);
  }

  // Process notification (with batching and smart display logic)
  processNotification(notification) {
    // Add to queue for batching if user is not viewing the tab
    if (!this.isVisible && this.preferences.batchDelay > 0) {
      this.notificationQueue.push(notification);
      this.scheduleBatchProcessing();
      return;
    }

    // Show immediately if tab is visible or no batching
    this.showNotification(notification);
  }

  // Schedule batch processing of queued notifications
  scheduleBatchProcessing() {
    if (this.batchTimeout) return; // Already scheduled

    this.batchTimeout = setTimeout(() => {
      this.processNotificationQueue();
      this.batchTimeout = null;
    }, this.preferences.batchDelay);
  }

  // Process queued notifications
  processNotificationQueue() {
    if (this.notificationQueue.length === 0) return;

    if (this.notificationQueue.length === 1) {
      // Single notification
      this.showNotification(this.notificationQueue[0]);
    } else {
      // Multiple notifications - create a summary
      const summary = this.createNotificationSummary(this.notificationQueue);
      this.showNotification(summary);
    }

    this.notificationQueue = [];
  }

  // Create summary notification for multiple notifications
  createNotificationSummary(notifications) {
    const categories = notifications.reduce((acc, notif) => {
      acc[notif.category] = (acc[notif.category] || 0) + 1;
      return acc;
    }, {});

    const categoryText = Object.entries(categories)
      .map(([cat, count]) => `${count} ${cat}`)
      .join(', ');

    return {
      id: `summary-${Date.now()}`,
      title: `📱 ${notifications.length} New Notifications`,
      message: `You have new updates: ${categoryText}`,
      type: 'info',
      category: 'summary',
      timestamp: new Date(),
      data: { notifications },
      actions: [
        { action: 'view_all', title: 'View All' }
      ]
    };
  }

  // Show notification using appropriate method
  async showNotification(notification) {
    // Always show in-app notification
    this.showInAppNotification(notification);

    // Show desktop/push notification if enabled and tab not visible
    if (this.preferences.showOnDesktop && !this.isVisible) {
      await this.showDesktopNotification(notification);
    }

    // Play sound if enabled
    if (this.preferences.sound) {
      this.playNotificationSound(notification.type);
    }

    // Vibrate if enabled and supported
    if (this.preferences.vibration && 'vibrate' in navigator) {
      navigator.vibrate([100, 50, 100]);
    }

    // Emit for other components to listen
    this.emit('notification', notification);
  }

  // Show in-app notification using existing system
  showInAppNotification(notification) {
    if (window.showNotification) {
      window.showNotification(notification.message, notification.type, 5000);
    }
  }

  // Show desktop/push notification
  async showDesktopNotification(notification) {
    try {
      // Request permission if needed
      if ('Notification' in window && Notification.permission === 'default') {
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') return;
      }

      if ('Notification' in window && Notification.permission === 'granted') {
        const options = {
          body: notification.message,
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          tag: notification.category,
          requireInteraction: notification.type === 'error',
          vibrate: this.preferences.vibration ? [100, 50, 100] : undefined,
          actions: notification.actions?.slice(0, 2) // Limit to 2 actions
        };

        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.ready;
          await registration.showNotification(notification.title, options);
        } else {
          new Notification(notification.title, options);
        }
      }
    } catch (error) {
      console.error('Failed to show desktop notification:', error);
    }
  }

  // Play notification sound
  playNotificationSound(type) {
    try {
      // Create audio context if needed
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      // Generate simple beep based on notification type
      const frequency = type === 'success' ? 800 : type === 'error' ? 400 : 600;
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);

      oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, this.audioContext.currentTime + 0.01);
      gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + 0.1);

      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + 0.1);
    } catch (error) {
      console.warn('Failed to play notification sound:', error);
    }
  }

  // Event listener system
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  // Disconnect WebSocket
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    this.stopHeartbeat();
    this.isConnected = false;
  }

  // Get connection status
  getStatus() {
    return {
      connected: this.isConnected,
      connectionFailed: this.connectionFailed,
      reconnectAttempts: this.reconnectAttempts,
      preferences: this.preferences,
      queuedNotifications: this.notificationQueue.length
    };
  }

  // Update preferences
  updatePreferences(newPreferences) {
    this.savePreferences(newPreferences);
  }
}

// Export singleton instance
export const realTimeNotifications = new RealTimeNotificationManager();

export default realTimeNotifications;
