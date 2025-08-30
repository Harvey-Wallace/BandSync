/**
 * WebSocket Context for Real-time Notifications
 * Manages WebSocket connection and provides notification functionality to React components
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io } from 'socket.io-client';
import { getApiUrl } from '../utils/apiUrl';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // disconnected, connecting, connected, error

  // Notification handlers
  const [onRSVPUpdate, setOnRSVPUpdate] = useState(() => () => {});
  const [onEventCreated, setOnEventCreated] = useState(() => () => {});
  const [onEventUpdated, setOnEventUpdated] = useState(() => () => {});
  const [eventHandlers, setEventHandlers] = useState({}); // Generic event handlers

  const connectSocket = useCallback(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No token available for WebSocket connection');
      setConnectionStatus('error');
      return;
    }

    setConnectionStatus('connecting');

    // Create socket connection
    const apiUrl = getApiUrl();
    const socketUrl = apiUrl.replace('/api', ''); // Remove /api suffix for socket connection
    
    console.log('Connecting to WebSocket at:', socketUrl);
    
    const newSocket = io(socketUrl, {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling'],
      timeout: 10000,
      forceNew: true
    });

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('WebSocket connected successfully');
      setIsConnected(true);
      setConnectionStatus('connected');
      setSocket(newSocket);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      setIsConnected(false);
      setConnectionStatus('disconnected');
      setSocket(null);
    });

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setIsConnected(false);
      setConnectionStatus('error');
      setSocket(null);
    });

    // Confirmation and status handlers
    newSocket.on('connection_confirmed', (data) => {
      console.log('Connection confirmed:', data);
      addNotification({
        type: 'info',
        message: 'Real-time notifications connected',
        timestamp: new Date().toISOString()
      });
    });

    newSocket.on('notification_status', (data) => {
      console.log('Notification status:', data);
    });

    // Real-time notification handlers
    newSocket.on('rsvp_updated', (data) => {
      console.log('RSVP update received:', data);
      addNotification({
        type: 'rsvp',
        message: data.message,
        data: data,
        timestamp: data.timestamp
      });
      
      // Call registered handler
      if (onRSVPUpdate) {
        onRSVPUpdate(data);
      }
    });

    newSocket.on('event_created', (data) => {
      console.log('Event created notification:', data);
      addNotification({
        type: 'event',
        message: data.message,
        data: data,
        timestamp: data.timestamp
      });
      
      // Call registered handler
      if (onEventCreated) {
        onEventCreated(data);
      }
    });

    newSocket.on('event_updated', (data) => {
      console.log('Event updated notification:', data);
      addNotification({
        type: 'event',
        message: data.message,
        data: data,
        timestamp: data.timestamp
      });
      
      // Call registered handler
      if (onEventUpdated) {
        onEventUpdated(data);
      }
    });

    // Member activity handler
    newSocket.on('member_activity', (data) => {
      console.log('Member activity received:', data);
      
      // Call generic event handler if registered
      if (eventHandlers.member_activity) {
        eventHandlers.member_activity(data);
      }
      
      // Also add as notification for important activities
      if (data.activity && ['high', 'medium'].includes(data.activity.priority)) {
        addNotification({
          type: 'activity',
          message: data.message,
          data: data,
          timestamp: data.activity.timestamp
        });
      }
    });

    // Keepalive ping/pong
    newSocket.on('pong', (data) => {
      console.log('Pong received:', data);
    });

    // Store socket reference
    setSocket(newSocket);

    return newSocket;
  }, [onRSVPUpdate, onEventCreated, onEventUpdated]);

  const disconnectSocket = useCallback(() => {
    if (socket) {
      console.log('Disconnecting WebSocket');
      socket.disconnect();
      setSocket(null);
      setIsConnected(false);
      setConnectionStatus('disconnected');
    }
  }, [socket]);

  const addNotification = useCallback((notification) => {
    const notificationWithId = {
      ...notification,
      id: Date.now() + Math.random(),
      read: false
    };
    
    setNotifications(prev => [notificationWithId, ...prev.slice(0, 49)]); // Keep last 50 notifications
    
    // Show browser notification if permission granted
    if (Notification.permission === 'granted') {
      new Notification(notification.message, {
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: notification.type
      });
    }
  }, []);

  const markNotificationAsRead = useCallback((notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const requestNotificationPermission = useCallback(async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
      return permission === 'granted';
    }
    return Notification.permission === 'granted';
  }, []);

  // Register event handlers
  const registerRSVPHandler = useCallback((handler) => {
    setOnRSVPUpdate(() => handler);
  }, []);

  const registerEventCreatedHandler = useCallback((handler) => {
    setOnEventCreated(() => handler);
  }, []);

  const registerEventUpdatedHandler = useCallback((handler) => {
    setOnEventUpdated(() => handler);
  }, []);

  // Generic event handler registration
  const registerEventHandler = useCallback((eventType, handler) => {
    setEventHandlers(prev => ({
      ...prev,
      [eventType]: handler
    }));
  }, []);

  // Send ping for keepalive
  const sendPing = useCallback(() => {
    if (socket && isConnected) {
      socket.emit('ping');
    }
  }, [socket, isConnected]);

  // Auto-connect when token is available
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token && !socket && connectionStatus === 'disconnected') {
      connectSocket();
    }
  }, [connectSocket, socket, connectionStatus]);

  // Setup keepalive ping
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(sendPing, 30000); // Ping every 30 seconds
      return () => clearInterval(pingInterval);
    }
  }, [isConnected, sendPing]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [socket]);

  const value = {
    // Connection state
    socket,
    isConnected,
    connectionStatus,
    
    // Connection methods
    connect: connectSocket,
    disconnect: disconnectSocket,
    
    // Notifications
    notifications,
    unreadCount: notifications.filter(n => !n.read).length,
    addNotification,
    markNotificationAsRead,
    clearNotifications,
    
    // Browser notifications
    requestNotificationPermission,
    
    // Event handlers
    registerRSVPHandler,
    registerEventCreatedHandler,
    registerEventUpdatedHandler,
    registerEventHandler, // Generic event handler registration
    
    // Utility
    sendPing
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
