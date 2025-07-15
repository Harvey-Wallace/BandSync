import 'react-app-polyfill/ie11';
import 'react-app-polyfill/stable';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

console.log('🚀 React index.js starting...');

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

console.log('✅ React app rendered');

// Temporarily disable service worker for iOS debugging
/*
// iOS-specific service worker registration
if ('serviceWorker' in navigator) {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  
  if (isIOS) {
    console.log('iOS detected, registering service worker with extra care...');
  }
  
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
        
        // Register for background sync (if supported)
        if ('sync' in window.ServiceWorkerRegistration.prototype) {
          console.log('Background sync supported');
        }
        
        // Request notification permission (be careful on iOS)
        if ('Notification' in window && 'PushManager' in window) {
          if (Notification.permission === 'default') {
            // On iOS, only request permission when user explicitly asks
            if (!isIOS) {
              Notification.requestPermission().then((permission) => {
                console.log('Notification permission:', permission);
              });
            }
          }
        }
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
        
        // On iOS, SW registration failure is not critical
        if (isIOS) {
          console.log('Service worker registration failed on iOS, continuing without SW...');
        }
      });
  });
} else {
  console.log('Service workers not supported in this browser');
}
*/
