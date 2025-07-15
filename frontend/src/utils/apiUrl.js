// Utility function to get API URL consistently across the app
export const getApiUrl = () => {
  let apiUrl = process.env.REACT_APP_API_URL || 
               window.ENV?.REACT_APP_API_URL || 
               'https://app.bandsync.co.uk/api';

  // iOS-specific debugging
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  
  if (isIOS) {
    console.log('iOS API URL determination:', {
      processEnv: process.env.REACT_APP_API_URL,
      windowEnv: window.ENV?.REACT_APP_API_URL,
      finalUrl: apiUrl,
      environment: process.env.NODE_ENV
    });
  }
  
  // Ensure URL doesn't have trailing slash
  apiUrl = apiUrl.replace(/\/+$/, '');
  
  return apiUrl;
};

export default getApiUrl;
