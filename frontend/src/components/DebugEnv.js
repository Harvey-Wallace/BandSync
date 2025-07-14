import React from 'react';

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

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">Environment Variables Debug</h5>
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
        <div className="mt-3">
          <h6>Google Maps Status:</h6>
          <p className={`alert ${
            process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? 'alert-success' : 'alert-danger'
          }`}>
            {process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? 
              '✅ Google Maps API Key is available' : 
              '❌ Google Maps API Key is missing'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default DebugEnv;
