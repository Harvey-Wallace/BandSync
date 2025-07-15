import React, { Component } from 'react';

class IOSErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null,
      isIOS: false
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    
    this.setState({
      error: error,
      errorInfo: errorInfo,
      isIOS: isIOS
    });

    // Log error for debugging
    console.error('iOS Error Boundary caught an error:', error, errorInfo);
    
    // Store error in localStorage for debugging
    try {
      localStorage.setItem('ios_error_log', JSON.stringify({
        error: error.toString(),
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      }));
    } catch (e) {
      console.warn('Could not save error to localStorage:', e);
    }
  }

  componentDidMount() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    this.setState({ isIOS });

    // Add iOS-specific event listeners
    if (isIOS) {
      window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
      window.addEventListener('error', this.handleError);
    }
  }

  componentWillUnmount() {
    if (this.state.isIOS) {
      window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
      window.removeEventListener('error', this.handleError);
    }
  }

  handleUnhandledRejection = (event) => {
    console.error('Unhandled Promise Rejection on iOS:', event.reason);
    this.setState({
      hasError: true,
      error: new Error(`Unhandled Promise Rejection: ${event.reason}`),
      errorInfo: { componentStack: 'Promise rejection' }
    });
  };

  handleError = (event) => {
    console.error('Global error on iOS:', event.error);
    this.setState({
      hasError: true,
      error: event.error || new Error(event.message),
      errorInfo: { 
        componentStack: `Global error at ${event.filename}:${event.lineno}:${event.colno}` 
      }
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24',
          fontFamily: 'monospace'
        }}>
          <h2>🚨 iOS Error Detected</h2>
          <details style={{ marginBottom: '10px' }}>
            <summary>Error Details</summary>
            <pre style={{ 
              backgroundColor: '#fff3cd',
              padding: '10px',
              borderRadius: '4px',
              fontSize: '12px',
              overflow: 'auto'
            }}>
              {this.state.error && this.state.error.toString()}
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </details>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Device Info:</strong><br />
            User Agent: {navigator.userAgent}<br />
            Is iOS: {this.state.isIOS.toString()}<br />
            Viewport: {window.innerWidth}x{window.innerHeight}<br />
            Environment: {process.env.NODE_ENV}<br />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <strong>Quick Actions:</strong><br />
            <button 
              onClick={() => window.location.reload()}
              style={{
                margin: '5px',
                padding: '10px 15px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🔄 Reload App
            </button>
            <button 
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              style={{
                margin: '5px',
                padding: '10px 15px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🗑️ Clear Data & Reload
            </button>
            <button 
              onClick={() => {
                const errorLog = localStorage.getItem('ios_error_log');
                if (errorLog) {
                  alert('Error log copied to clipboard (if supported)');
                  if (navigator.clipboard) {
                    navigator.clipboard.writeText(errorLog);
                  }
                }
              }}
              style={{
                margin: '5px',
                padding: '10px 15px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              📋 Copy Error Log
            </button>
          </div>

          <div style={{ fontSize: '12px', marginTop: '10px' }}>
            <strong>Troubleshooting Tips:</strong>
            <ul>
              <li>Try refreshing the page</li>
              <li>Clear your browser cache and cookies</li>
              <li>Check your internet connection</li>
              <li>Try opening the app in private/incognito mode</li>
              <li>Update your iOS and Safari browser</li>
            </ul>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default IOSErrorBoundary;
