# Google Maps Integration Setup Guide

This guide will help you set up Google Maps integration for the BandSync event location features.

## Features Included

- **Address Autocomplete**: Search and select locations using Google Places API
- **Interactive Map**: Visual map with draggable pins for precise location placement
- **Automatic Geocoding**: Convert addresses to coordinates and vice versa
- **Map Links**: Direct links to Google Maps for easy navigation

## Setup Instructions

### 1. Get a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Maps JavaScript API**
   - **Places API**
   - **Geocoding API**

4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### 2. Configure API Key Restrictions (Recommended)

For security, restrict your API key:

1. In the Google Cloud Console, click on your API key
2. Under "Application restrictions":
   - Choose "HTTP referrers (web sites)"
   - Add your domains:
     - `http://localhost:3000/*` (for development)
     - `https://yourdomain.com/*` (for production)

3. Under "API restrictions":
   - Choose "Restrict key"
   - Select only the APIs you enabled above

### 3. Add API Key to Environment

1. Open `/frontend/.env`
2. Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` with your actual API key:

```env
REACT_APP_GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

### 4. Restart the Development Server

After updating the environment file:

```bash
cd frontend
npm start
```

## Usage

### Creating Events with Locations

1. Click "Create Event" as an admin
2. Fill in the event details including:
   - **Title**: Name of your event
   - **Type**: Choose from Rehearsal, Concert, Committee Meeting, or AGM
   - **Description**: Additional event information
   - **Date & Time**: When the event occurs
   - **Location**: Start typing to search for places

3. **Using the Map**:
   - The map will automatically show when you enter a location
   - Click anywhere on the map to set a precise location
   - Drag the pin to adjust the exact position
   - The address will update automatically when you move the pin

### Event Display

Events will now show:
- Event type badges with color coding
- Separate time display
- Enhanced location information
- "View on Map" links for events with coordinates

## Troubleshooting

### Map Not Loading
- Check that your API key is correct in `.env`
- Verify that the required APIs are enabled in Google Cloud Console
- Check the browser console for error messages

### Address Search Not Working
- Ensure the Places API is enabled
- Check API key restrictions

### Getting "This page can't load Google Maps correctly"
- Usually indicates billing is not set up in Google Cloud Console
- Google Maps requires a billing account even for free tier usage

## Cost Information

Google Maps APIs have a free tier with generous limits:
- **Maps JavaScript API**: 28,000 map loads per month free
- **Places API**: $2.83-$4.85 per 1,000 requests after free tier
- **Geocoding API**: $2.00 per 1,000 requests after free tier

For most small organizations, usage will likely stay within the free tier.

## Fallback Behavior

If no Google Maps API key is provided:
- The map section will not display
- Address autocomplete will not work
- Basic location text input will still function
- Event display will show location text without map links

This allows the application to work without Google Maps if needed.
