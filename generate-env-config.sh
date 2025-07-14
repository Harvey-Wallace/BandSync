#!/bin/bash

# Generate environment configuration for React build
echo "🔧 Generating environment configuration..."

# Create the env-config.js file with actual values
cat > frontend/public/env-config.js << 'EOF'
// Runtime environment configuration
window.ENV = {
  REACT_APP_API_URL: 'https://bandsync-production.up.railway.app',
  REACT_APP_GOOGLE_MAPS_API_KEY: 'AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc',
  NODE_ENV: 'production'
};

// Inject into process.env for React components
if (typeof window !== 'undefined') {
  window.process = window.process || {};
  window.process.env = window.process.env || {};
  Object.assign(window.process.env, window.ENV);
}

console.log('🔧 Environment configuration loaded:', window.ENV);
EOF

echo "✅ Environment configuration generated"
