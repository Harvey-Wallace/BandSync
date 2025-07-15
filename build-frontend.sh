#!/bin/bash

# Build script that injects Railway environment variables into React build
echo "🔧 Setting up environment variables for React build..."

# Create a temporary .env file with Railway environment variables
cat > frontend/.env.production.local << EOF
REACT_APP_API_URL=${REACT_APP_API_URL:-https://app.bandsync.co.uk/api}
REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY:-}
EOF

echo "📝 Created frontend/.env.production.local with:"
echo "REACT_APP_API_URL=${REACT_APP_API_URL:-https://app.bandsync.co.uk/api}"
echo "REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY:+SET}"

# Build the React app
echo "🏗️ Building React app..."
cd frontend
npm install
npm run build

echo "✅ React build complete!"
