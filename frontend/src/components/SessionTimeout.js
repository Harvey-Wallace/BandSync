import React, { useState, useEffect, useRef } from 'react';
import apiClient from '../utils/api';

const SessionTimeout = () => {
  const [showWarning, setShowWarning] = useState(false);
  const [countdown, setCountdown] = useState(120); // 2 minutes warning
  const [isActive, setIsActive] = useState(false);
  const timeoutRef = useRef(null);
  const warningTimeoutRef = useRef(null);
  const countdownRef = useRef(null);

  // Token expires in 20 minutes, show warning at 18 minutes (2 minutes before expiry)
  const TOKEN_LIFETIME = 20 * 60 * 1000; // 20 minutes in milliseconds
  const WARNING_TIME = 2 * 60 * 1000; // 2 minutes before expiry

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      startSession();
    }

    // Listen for login events
    const handleLogin = () => startSession();
    const handleLogout = () => stopSession();
    
    window.addEventListener('userLogin', handleLogin);
    window.addEventListener('userLogout', handleLogout);

    return () => {
      stopSession();
      window.removeEventListener('userLogin', handleLogin);
      window.removeEventListener('userLogout', handleLogout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startSession = () => {
    stopSession(); // Clear any existing timers
    setIsActive(true);
    
    // Set warning timer (18 minutes after login)
    warningTimeoutRef.current = setTimeout(() => {
      setShowWarning(true);
      setCountdown(120); // 2 minutes countdown
      startCountdown();
    }, TOKEN_LIFETIME - WARNING_TIME);
  };

  const stopSession = () => {
    setIsActive(false);
    setShowWarning(false);
    setCountdown(120);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (warningTimeoutRef.current) {
      clearTimeout(warningTimeoutRef.current);
      warningTimeoutRef.current = null;
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      countdownRef.current = null;
    }
  };

  const startCountdown = () => {
    countdownRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          // Time's up, logout user
          handleLogout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleStayLoggedIn = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post('/api/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`,
        },
      });

      const { access_token, role, organization_id, organization } = response.data;

      // Update stored tokens and user info
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      if (organization_id) localStorage.setItem('organization_id', organization_id);
      if (organization) localStorage.setItem('organization', organization);

      // Restart the session timer
      setShowWarning(false);
      startSession();

      // Dispatch event to update navbar and other components
      window.dispatchEvent(new CustomEvent('userLogin'));
      
    } catch (error) {
      console.error('Failed to refresh token:', error);
      handleLogout();
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    stopSession();
    window.dispatchEvent(new CustomEvent('userLogout'));
    window.location.href = '/login';
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Reset timers on user activity
  useEffect(() => {
    const resetTimer = () => {
      if (isActive && !showWarning) {
        startSession();
      }
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    events.forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetTimer, true);
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, showWarning]);

  if (!showWarning) return null;

  return (
    <div className="session-timeout-overlay">
      <div className="session-timeout-modal">
        <div className="modal-content">
          <h4 className="text-warning">
            <i className="fas fa-exclamation-triangle me-2"></i>
            Session Expiring Soon
          </h4>
          <p className="mb-3">
            Your session will expire in <strong className="text-danger">{formatTime(countdown)}</strong>
          </p>
          <p className="text-muted small mb-4">
            You will be automatically logged out when the timer reaches zero.
          </p>
          <div className="d-flex justify-content-center gap-3">
            <button 
              className="btn btn-primary"
              onClick={handleStayLoggedIn}
              disabled={countdown <= 0}
            >
              <i className="fas fa-refresh me-2"></i>
              Stay Logged In
            </button>
            <button 
              className="btn btn-outline-secondary"
              onClick={handleLogout}
            >
              <i className="fas fa-sign-out-alt me-2"></i>
              Logout Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeout;
