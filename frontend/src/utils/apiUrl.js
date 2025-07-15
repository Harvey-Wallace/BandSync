// Utility function to get API URL consistently across the app
export const getApiUrl = () => {
  return process.env.REACT_APP_API_URL || 
         window.ENV?.REACT_APP_API_URL || 
         'https://app.bandsync.co.uk/api';
};

export default getApiUrl;
