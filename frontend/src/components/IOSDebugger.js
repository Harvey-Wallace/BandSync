import React, { useState, useEffect } from 'react';

function IOSDebugger() {
  const [debugInfo, setDebugInfo] = useState({
    userAgent: '',
    isIOS: false,
    isStandalone: false,
    viewportWidth: 0,
    viewportHeight: 0,
    errors: [],
    warnings: [],
    apiUrl: '',
    apiReachable: false,
    consoleOutput: []
  });

  useEffect(() => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isStandalone = window.navigator.standalone === true;
    
    // Capture console output
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const consoleBuffer = [];
    
    console.log = (...args) => {
      consoleBuffer.push({ type: 'log', message: args.join(' '), timestamp: new Date().toISOString() });
      originalLog.apply(console, args);
    };
    
    console.error = (...args) => {
      consoleBuffer.push({ type: 'error', message: args.join(' '), timestamp: new Date().toISOString() });
      originalError.apply(console, args);
    };
    
    console.warn = (...args) => {
      consoleBuffer.push({ type: 'warn', message: args.join(' '), timestamp: new Date().toISOString() });
      originalWarn.apply(console, args);
    };

    // Test API reachability
    const testApiReachability = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || window.ENV?.REACT_APP_API_URL || 'https://app.bandsync.co.uk/api';
        const response = await fetch(`${apiUrl}/health`, { method: 'GET' });
        return { apiUrl, reachable: response.ok };
      } catch (error) {
        console.error('API reachability test failed:', error);
        return { apiUrl: 'Failed to determine', reachable: false };
      }
    };

    const initializeDebugInfo = async () => {
      const apiTest = await testApiReachability();
      
      setDebugInfo({
        userAgent: navigator.userAgent,
        isIOS: isIOS,
        isStandalone: isStandalone,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        errors: [],
        warnings: [],
        apiUrl: apiTest.apiUrl,
        apiReachable: apiTest.reachable,
        consoleOutput: consoleBuffer.slice(-20) // Last 20 console messages
      });
    };

    initializeDebugInfo();

    // Error handling
    window.addEventListener('error', (event) => {
      setDebugInfo(prev => ({
        ...prev,
        errors: [...prev.errors, {
          message: event.message,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          stack: event.error?.stack
        }]
      }));
    });

    window.addEventListener('unhandledrejection', (event) => {
      setDebugInfo(prev => ({
        ...prev,
        errors: [...prev.errors, {
          message: `Unhandled Promise Rejection: ${event.reason}`,
          type: 'promise'
        }]
      }));
    });

    // Viewport change detection
    const handleResize = () => {
      setDebugInfo(prev => ({
        ...prev,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight
      }));
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('error', () => {});
      window.removeEventListener('unhandledrejection', () => {});
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
      
      // Restore original console methods
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
    };
  }, []);

  const isIOS = debugInfo.isIOS;

  if (!isIOS) {
    return null; // Only show on iOS devices
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.9)',
      color: 'white',
      padding: '10px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      overflow: 'auto'
    }}>
      <div style={{ marginBottom: '10px' }}>
        <strong>🐛 iOS Debug Information</strong>
        <button 
          onClick={() => window.location.reload()}
          style={{
            float: 'right',
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '5px 10px',
            borderRadius: '3px'
          }}
        >
          Reload
        </button>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Device Info:</strong><br />
        User Agent: {debugInfo.userAgent}<br />
        Is iOS: {debugInfo.isIOS.toString()}<br />
        Is Standalone: {debugInfo.isStandalone.toString()}<br />
        Viewport: {debugInfo.viewportWidth}x{debugInfo.viewportHeight}<br />
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>API Info:</strong><br />
        API URL: {debugInfo.apiUrl}<br />
        API Reachable: {debugInfo.apiReachable.toString()}<br />
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>Environment:</strong><br />
        NODE_ENV: {process.env.NODE_ENV}<br />
        REACT_APP_API_URL: {process.env.REACT_APP_API_URL || 'undefined'}<br />
        Window ENV: {JSON.stringify(window.ENV || {}, null, 2)}<br />
      </div>

      {debugInfo.errors.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <strong>❌ Errors ({debugInfo.errors.length}):</strong><br />
          {debugInfo.errors.map((error, index) => (
            <div key={index} style={{ background: '#800', padding: '5px', margin: '2px 0' }}>
              {error.message}<br />
              {error.filename && <small>File: {error.filename}:{error.lineno}</small>}<br />
              {error.stack && <small>Stack: {error.stack.substring(0, 200)}...</small>}
            </div>
          ))}
        </div>
      )}

      <div style={{ marginBottom: '10px' }}>
        <strong>📝 Console Output:</strong><br />
        <div style={{ maxHeight: '200px', overflow: 'auto', background: '#111', padding: '5px' }}>
          {debugInfo.consoleOutput.map((entry, index) => (
            <div key={index} style={{ 
              color: entry.type === 'error' ? '#ff6b6b' : entry.type === 'warn' ? '#ffd93d' : '#6bcf7f',
              fontSize: '10px',
              marginBottom: '2px'
            }}>
              [{entry.timestamp.split('T')[1].split('.')[0]}] {entry.type.toUpperCase()}: {entry.message}
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>🧪 Quick Tests:</strong><br />
        <button 
          onClick={() => {
            try {
              localStorage.setItem('test', 'value');
              localStorage.removeItem('test');
              alert('✅ localStorage works');
            } catch (e) {
              alert('❌ localStorage failed: ' + e.message);
            }
          }}
          style={{ margin: '2px', padding: '5px', fontSize: '10px' }}
        >
          Test localStorage
        </button>
        <button 
          onClick={() => {
            fetch('/manifest.json')
              .then(r => r.json())
              .then(data => alert('✅ Manifest loaded: ' + data.name))
              .catch(e => alert('❌ Manifest failed: ' + e.message));
          }}
          style={{ margin: '2px', padding: '5px', fontSize: '10px' }}
        >
          Test Manifest
        </button>
        <button 
          onClick={() => {
            const apiUrl = debugInfo.apiUrl;
            fetch(`${apiUrl}/health`)
              .then(r => r.ok ? alert('✅ API reachable') : alert('❌ API returned ' + r.status))
              .catch(e => alert('❌ API failed: ' + e.message));
          }}
          style={{ margin: '2px', padding: '5px', fontSize: '10px' }}
        >
          Test API
        </button>
      </div>
    </div>
  );
}

export default IOSDebugger;
