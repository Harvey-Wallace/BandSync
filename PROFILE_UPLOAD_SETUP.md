# Profile Picture Upload Setup Guide

## Cloudinary Setup (Free tier available)

### 1. Create a Cloudinary Account
1. Go to [https://cloudinary.com](https://cloudinary.com)
2. Sign up for a free account
3. Verify your email address

### 2. Get Your Credentials
1. Go to your Cloudinary Dashboard
2. Copy the following values:
   - **Cloud Name**
   - **API Key** 
   - **API Secret**

### 3. Configure Environment Variables
1. Create a `.env` file in the `backend` folder (or update existing one)
2. Add these variables:
```
CLOUDINARY_CLOUD_NAME=di0gom1vd
CLOUDINARY_API_KEY=982593917724433
CLOUDINARY_API_SECRET=oGCqi0PHPSR8wOPce5WX1XSoZkY
```

### 4. Restart the Backend Server
```bash
cd backend
python app.py
```

## Features Implemented

### ✅ File Upload
- Drag & drop or browse for files
- Supports PNG, JPG, JPEG, GIF, WebP
- Maximum file size: 5MB
- Automatic image optimization and resizing (300x300px)

### ✅ Smart Cropping
- Automatically crops images to focus on faces
- Maintains aspect ratio
- Optimizes file size and quality

### ✅ Fallback Option
- Users can still provide URLs if they prefer
- File upload takes priority over URL

### ✅ Preview
- Real-time preview of selected images
- Shows current avatar in profile bubble

## Usage
1. Go to Profile page
2. Click "Choose File" to select an image
3. Preview appears immediately
4. Click "Update Profile" to save
5. Image is uploaded to Cloudinary and URL is saved to database

## Free Tier Limits
- 25 GB storage
- 25 GB monthly bandwidth
- 25,000 monthly transformations

Perfect for small to medium applications!
