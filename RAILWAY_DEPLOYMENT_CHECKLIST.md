# Railway Deployment Checklist

## Required Environment Variables

Before deploying to Railway, ensure these environment variables are set in the Railway dashboard:

### Backend Variables
- `FLASK_ENV=production` ✅ (already set in railway.toml)
- `DATABASE_URL` (if using external database)
- `SECRET_KEY` (for Flask sessions)

### Frontend Variables (Required for Build)
- `REACT_APP_API_URL` (your Railway app URL)
- `REACT_APP_GOOGLE_MAPS_API_KEY` (Google Maps API key)

## Setting Environment Variables in Railway

1. Go to your Railway project dashboard
2. Select your service
3. Navigate to "Variables" tab
4. Click "New Variable"
5. Add each variable with its value
6. **Important**: Variables starting with `REACT_APP_` must be set BEFORE building

## Deployment Process

1. ✅ Set all required environment variables in Railway dashboard
2. ✅ Commit and push changes to your repository
3. ✅ Railway will automatically trigger a build
4. ✅ Monitor the build logs for any environment variable warnings
5. ✅ Test the deployed application

## Troubleshooting

### Google Maps Not Working
- Check that `REACT_APP_GOOGLE_MAPS_API_KEY` is set in Railway dashboard
- Verify the API key is valid and has required permissions
- Check that the following APIs are enabled in Google Cloud Console:
  - Maps JavaScript API
  - Places API
  - Geocoding API

### API Calls Failing
- Verify `REACT_APP_API_URL` is set correctly
- Check that the URL matches your Railway app URL
- Ensure the URL includes protocol (https://)

## Build Process

The build process (`nixpacks.toml`) will:
1. Run environment variable checks
2. Install frontend dependencies
3. Build the React app (environment variables are compiled into the build)
4. Copy built files to backend static directory
5. Install backend dependencies
6. Start the Flask application

## Important Notes

- React environment variables are compiled into the build at build time
- Changes to `REACT_APP_*` variables require a rebuild
- The `.env` file is only used for local development
- Production environment variables must be set in Railway dashboard
