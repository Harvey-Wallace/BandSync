// Configuration file for runtime environment variables
// This file is generated during the build process
window.ENV = {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL || 'https://bandsync-production.up.railway.app',
  REACT_APP_GOOGLE_MAPS_API_KEY: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '',
  NODE_ENV: process.env.NODE_ENV || 'production'
};

// Make it available globally
window.process = window.process || {};
window.process.env = window.process.env || {};
Object.assign(window.process.env, window.ENV);

console.log('🔧 Runtime configuration loaded:', window.ENV);
