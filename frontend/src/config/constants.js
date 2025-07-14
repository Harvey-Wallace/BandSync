// Application configuration constants
// This file contains hardcoded values for production deployment

export const APP_CONFIG = {
  API_URL: 'https://bandsync-production.up.railway.app',
  GOOGLE_MAPS_API_KEY: 'AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc',
  NODE_ENV: 'production'
};

// Fallback for process.env access
export const getApiUrl = () => {
  return process.env.REACT_APP_API_URL || APP_CONFIG.API_URL;
};

export const getGoogleMapsApiKey = () => {
  return process.env.REACT_APP_GOOGLE_MAPS_API_KEY || APP_CONFIG.GOOGLE_MAPS_API_KEY;
};

export const isProduction = () => {
  return process.env.NODE_ENV === 'production' || APP_CONFIG.NODE_ENV === 'production';
};

// Make config available globally for debugging
if (typeof window !== 'undefined') {
  window.APP_CONFIG = APP_CONFIG;
}
