import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Alert, Row, Col } from 'react-bootstrap';
import { networkManager, notificationManager, installManager, offlineManager } from '../utils/offline';

const PWAStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [canInstall, setCanInstall] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState(
    typeof Notification !== 'undefined' ? Notification.permission : 'denied'
  );
  const [offlineRSVPs, setOfflineRSVPs] = useState([]);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    // Network status listener
    const handleNetworkChange = (status) => {
      setIsOnline(status === 'online');
    };

    networkManager.addListener(handleNetworkChange);

    // Check install status
    setCanInstall(installManager.canInstall());
    setIsInstalled(installManager.isInstalled);

    // Check for offline RSVPs
    loadOfflineRSVPs();

    // Check if we should show install prompt
    const installPromptShown = localStorage.getItem('installPromptShown');
    if (!installPromptShown && installManager.canInstall()) {
      setShowInstallPrompt(true);
    }

    return () => {
      networkManager.removeListener(handleNetworkChange);
    };
  }, []);

  const loadOfflineRSVPs = async () => {
    const rsvps = await offlineManager.getOfflineRSVPs();
    setOfflineRSVPs(rsvps);
  };

  const handleInstallApp = async () => {
    const installed = await installManager.promptInstall();
    if (installed) {
      setCanInstall(false);
      setIsInstalled(true);
    }
    setShowInstallPrompt(false);
    localStorage.setItem('installPromptShown', 'true');
  };

  const handleEnableNotifications = async () => {
    const granted = await notificationManager.requestPermission();
    if (granted) {
      setNotificationPermission('granted');
      await notificationManager.subscribeToNotifications();
    }
  };

  const handleDismissInstallPrompt = () => {
    setShowInstallPrompt(false);
    localStorage.setItem('installPromptShown', 'true');
  };

  return (
    <div className="pwa-status">
      {/* Install Prompt */}
      {showInstallPrompt && (
        <Alert variant="info" className="mb-3">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <strong>Install BandSync</strong>
              <p className="mb-0">Install BandSync as an app for quick access and offline features!</p>
            </div>
            <div>
              <Button variant="primary" size="sm" onClick={handleInstallApp} className="me-2">
                Install
              </Button>
              <Button variant="outline-secondary" size="sm" onClick={handleDismissInstallPrompt}>
                Later
              </Button>
            </div>
          </div>
        </Alert>
      )}

      <Card>
        <Card.Header>
          <h5 className="mb-0">App Status</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <div className="mb-3">
                <strong>Connection Status:</strong>{' '}
                <Badge bg={isOnline ? 'success' : 'warning'}>
                  {isOnline ? 'Online' : 'Offline'}
                </Badge>
              </div>
              
              <div className="mb-3">
                <strong>Installation:</strong>{' '}
                {isInstalled ? (
                  <Badge bg="success">Installed</Badge>
                ) : canInstall ? (
                  <div>
                    <Badge bg="info">Available</Badge>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="ms-2"
                      onClick={handleInstallApp}
                    >
                      Install App
                    </Button>
                  </div>
                ) : (
                  <Badge bg="secondary">Not Available</Badge>
                )}
              </div>

              <div className="mb-3">
                <strong>Notifications:</strong>{' '}
                <Badge bg={notificationPermission === 'granted' ? 'success' : 'warning'}>
                  {notificationPermission === 'granted' ? 'Enabled' : 'Disabled'}
                </Badge>
                {notificationPermission !== 'granted' && (
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="ms-2"
                    onClick={handleEnableNotifications}
                  >
                    Enable
                  </Button>
                )}
              </div>
            </Col>
            
            <Col md={6}>
              <div className="mb-3">
                <strong>Offline RSVPs:</strong>{' '}
                <Badge bg={offlineRSVPs.length > 0 ? 'warning' : 'success'}>
                  {offlineRSVPs.length}
                </Badge>
                {offlineRSVPs.length > 0 && (
                  <div className="mt-2">
                    <small className="text-muted">
                      {offlineRSVPs.length} RSVP(s) will sync when you're back online
                    </small>
                  </div>
                )}
              </div>

              <div className="mb-3">
                <strong>Service Worker:</strong>{' '}
                <Badge bg={navigator.serviceWorker ? 'success' : 'danger'}>
                  {navigator.serviceWorker ? 'Active' : 'Not Supported'}
                </Badge>
              </div>

              <div className="mb-3">
                <strong>Background Sync:</strong>{' '}
                <Badge bg={
                  'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype 
                    ? 'success' 
                    : 'warning'
                }>
                  {
                    'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype
                      ? 'Supported'
                      : 'Not Supported'
                  }
                </Badge>
              </div>
            </Col>
          </Row>

          {!isOnline && (
            <Alert variant="warning" className="mt-3">
              <strong>Offline Mode</strong>
              <p className="mb-0">
                You're currently offline. You can still view cached events and submit RSVPs, 
                which will sync automatically when you're back online.
              </p>
            </Alert>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default PWAStatus;
