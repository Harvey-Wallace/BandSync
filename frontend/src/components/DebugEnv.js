import React from 'react';
import { APP_CONFIG, getApiUrl, getGoogleMapsApiKey } from '../config/constants';

const DebugEnv = () => {
  const envVars = {
    NODE_ENV: process.env.NODE_ENV,
    REACT_APP_API_URL: process.env.REACT_APP_API_URL,
    REACT_APP_GOOGLE_MAPS_API_KEY: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
    // Show all REACT_APP_ variables
    ...Object.keys(process.env)
      .filter(key => key.startsWith('REACT_APP_'))
      .reduce((obj, key) => {
        obj[key] = process.env[key];
        return obj;
      }, {})
  };

  // Check fallback configurations
  const fallbackConfig = {
    'APP_CONFIG.API_URL': APP_CONFIG.API_URL,
    'APP_CONFIG.GOOGLE_MAPS_API_KEY': APP_CONFIG.GOOGLE_MAPS_API_KEY,
    'getApiUrl()': getApiUrl(),
    'getGoogleMapsApiKey()': getGoogleMapsApiKey(),
    'window.ENV': typeof window !== 'undefined' ? window.ENV : undefined,
    'window.APP_CONFIG': typeof window !== 'undefined' ? window.APP_CONFIG : undefined
  };

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">Environment Variables Debug</h5>
        
        <h6 className="mt-4">Environment Variables</h6>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Value</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(envVars).map(([key, value]) => (
                <tr key={key}>
                  <td><code>{key}</code></td>
                  <td>
                    {value ? (
                      <span className="text-success">
                        {key.includes('API_KEY') ? 
                          `${value.substring(0, 8)}...` : 
                          value
                        }
                      </span>
                    ) : (
                      <span className="text-danger">undefined</span>
                    )}
                  </td>
                  <td>
                    {value ? (
                      <span className="badge bg-success">SET</span>
                    ) : (
                      <span className="badge bg-danger">MISSING</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h6 className="mt-4">Fallback Configuration</h6>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Source</th>
                <th>Value</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(fallbackConfig).map(([key, value]) => (
                <tr key={key}>
                  <td><code>{key}</code></td>
                  <td>
                    {value ? (
                      <span className="text-success">
                        {key.includes('API_KEY') || key.includes('GOOGLE_MAPS') ? 
                          `${String(value).substring(0, 8)}...` : 
                          String(value)
                        }
                      </span>
                    ) : (
                      <span className="text-danger">undefined</span>
                    )}
                  </td>
                  <td>
                    {value ? (
                      <span className="badge bg-success">SET</span>
                    ) : (
                      <span className="badge bg-danger">MISSING</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-3">
          <h6>Google Maps Status:</h6>
          <p className={`alert ${
            getGoogleMapsApiKey() ? 'alert-success' : 'alert-danger'
          }`}>
            {getGoogleMapsApiKey() ? 
              '✅ Google Maps API Key is available (via fallback)' : 
              '❌ Google Maps API Key is missing'
            }
          </p>
          
          <h6>API URL Status:</h6>
          <p className={`alert ${
            getApiUrl() ? 'alert-success' : 'alert-danger'
          }`}>
            {getApiUrl() ? 
              `✅ API URL is available: ${getApiUrl()}` : 
              '❌ API URL is missing'
            }
          </p>
        </div>

        <div className="mt-3">
          <h6>Console Test:</h6>
          <button 
            className="btn btn-primary" 
            onClick={() => {
              console.log('=== DEBUG TEST ===');
              console.log('process.env.REACT_APP_GOOGLE_MAPS_API_KEY:', process.env.REACT_APP_GOOGLE_MAPS_API_KEY);
              console.log('getGoogleMapsApiKey():', getGoogleMapsApiKey());
              console.log('APP_CONFIG:', APP_CONFIG);
              console.log('window.ENV:', window.ENV);
              console.log('window.APP_CONFIG:', window.APP_CONFIG);
            }}
          >
            Log to Console
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugEnv;
