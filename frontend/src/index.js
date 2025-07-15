import 'react-app-polyfill/ie11';
import 'react-app-polyfill/stable';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
        
        // Register for background sync
        if ('sync' in window.ServiceWorkerRegistration.prototype) {
          console.log('Background sync supported');
        }
        
        // Request notification permission
        if ('Notification' in window && 'PushManager' in window) {
          if (Notification.permission === 'default') {
            Notification.requestPermission().then((permission) => {
              console.log('Notification permission:', permission);
            });
          }
        }
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}
