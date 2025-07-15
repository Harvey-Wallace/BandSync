import React, { useEffect, useState } from 'react';

const EnvironmentDebugger = () => {
  const [envVars, setEnvVars] = useState({});

  useEffect(() => {
    // Check various ways the environment variables might be loaded
    const envInfo = {
      processEnv: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
      windowEnv: window.ENV?.REACT_APP_GOOGLE_MAPS_API_KEY,
      windowProcess: window.process?.env?.REACT_APP_GOOGLE_MAPS_API_KEY,
      hasWindow: typeof window !== 'undefined',
      hasWindowEnv: typeof window !== 'undefined' && window.ENV,
      hasWindowProcess: typeof window !== 'undefined' && window.process,
      allWindowEnv: window.ENV,
      allProcessEnv: { ...process.env }
    };
    
    setEnvVars(envInfo);
    
    // Log to console for debugging
    console.log('🔍 Environment Debug Info:', envInfo);
  }, []);

  return (
    <div className="card mt-3">
      <div className="card-header">
        <h6>Environment Variables Debug</h6>
      </div>
      <div className="card-body">
        <div className="row">
          <div className="col-md-6">
            <h6>Google Maps API Key Sources:</h6>
            <ul>
              <li>process.env: {envVars.processEnv || 'Not found'}</li>
              <li>window.ENV: {envVars.windowEnv || 'Not found'}</li>
              <li>window.process.env: {envVars.windowProcess || 'Not found'}</li>
            </ul>
          </div>
          <div className="col-md-6">
            <h6>Environment Status:</h6>
            <ul>
              <li>Has window: {envVars.hasWindow ? '✅' : '❌'}</li>
              <li>Has window.ENV: {envVars.hasWindowEnv ? '✅' : '❌'}</li>
              <li>Has window.process: {envVars.hasWindowProcess ? '✅' : '❌'}</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-3">
          <h6>All window.ENV:</h6>
          <pre className="bg-light p-2">
            {JSON.stringify(envVars.allWindowEnv, null, 2)}
          </pre>
        </div>
        
        <div className="mt-3">
          <h6>All process.env (React):</h6>
          <pre className="bg-light p-2" style={{ maxHeight: '200px', overflow: 'auto' }}>
            {JSON.stringify(envVars.allProcessEnv, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default EnvironmentDebugger;
