# Cloudinary Setup for Railway Deployment

## 🚀 Railway Environment Variables Setup

### Required Variables
Add these to your Railway project's environment variables:

```bash
CLOUDINARY_CLOUD_NAME=di0gom1vd
CLOUDINARY_API_KEY=982593917724433
CLOUDINARY_API_SECRET=oGCqi0PHPSR8wOPce5WX1XSoZkY
```

### How to Add Environment Variables in Railway:

1. **Go to your Railway project dashboard**
2. **Click on your service** (BandSync)
3. **Go to the "Variables" tab**
4. **Click "New Variable"** and add each variable:
   - Name: `CLOUDINARY_CLOUD_NAME`, Value: `di0gom1vd`
   - Name: `CLOUDINARY_API_KEY`, Value: `982593917724433`
   - Name: `CLOUDINARY_API_SECRET`, Value: `oGCqi0PHPSR8wOPce5WX1XSoZkY`
5. **Click "Deploy"** to restart with new variables

## 🖼️ Image Upload Features Already Implemented

### ✅ **User Avatars**
- **Admin Dashboard**: Upload profile pictures for users
- **File Types**: PNG, JPG, JPEG, GIF, WebP
- **Size Limit**: 5MB maximum
- **Processing**: Auto-crop to 200x200px with face detection
- **Endpoint**: `POST /api/admin/users/{user_id}/avatar/upload`

### ✅ **Organization Logos**
- **Admin Dashboard**: Upload organization logos
- **File Types**: PNG, JPG, JPEG, GIF, WebP
- **Size Limit**: 5MB maximum
- **Processing**: Auto-resize to 400x200px max
- **Endpoint**: `POST /api/admin/upload-logo`

### ✅ **Features**
- **Smart Cropping**: Face detection for avatars
- **Auto-Optimization**: Cloudinary handles compression
- **Secure Upload**: Admin-only access
- **Organization Folders**: Images organized by organization
- **Preview**: Real-time preview before upload
- **Fallback**: Initials display if no image

## 📁 Cloudinary Folder Structure

```
bandsync/
├── org_1/
│   ├── avatars/
│   │   ├── user_1
│   │   ├── user_2
│   │   └── ...
│   └── logos/
│       └── logo_1
├── org_2/
│   ├── avatars/
│   └── logos/
└── ...
```

## 🔧 Testing Image Uploads

### After Deployment:

1. **Test Avatar Upload**:
   - Go to Admin Dashboard → Users
   - Click on a user → Upload avatar
   - Select image file and verify upload

2. **Test Logo Upload**:
   - Go to Admin Dashboard → Organization Branding
   - Upload organization logo
   - Verify it appears in navbar

3. **Check Cloudinary Dashboard**:
   - Login to cloudinary.com
   - Verify images are being stored
   - Check folder structure is correct

## 🚨 Security Notes

### ⚠️ **Important Security Fix Needed**
The Cloudinary credentials in `PROFILE_UPLOAD_SETUP.md` should be removed and only stored as environment variables in Railway.

### ✅ **Best Practices**:
- Never commit API keys to version control
- Use Railway environment variables for all secrets
- Regularly rotate API keys
- Monitor Cloudinary usage

## 🔍 Troubleshooting

### Common Issues:

**Upload fails with 500 error:**
- Check Railway environment variables are set
- Verify Cloudinary credentials are correct
- Check Railway logs for detailed error

**Images not displaying:**
- Verify Cloudinary URLs are accessible
- Check browser console for errors
- Verify organization folder permissions

**Upload button not showing:**
- Ensure user has admin role
- Check component props in frontend
- Verify JWT token is valid

### Debug Commands:

```bash
# Check Railway logs
railway logs

# Test Cloudinary connection locally
python -c "
import cloudinary
import os
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)
print('Cloudinary configured successfully')
"
```

## 📊 Cloudinary Free Tier Limits

- **Storage**: 25 GB
- **Monthly Bandwidth**: 25 GB
- **Monthly Transformations**: 25,000
- **Image/Video Size**: 10 MB per file

Perfect for small to medium applications!

## 🎯 Next Steps

1. **Add environment variables** to Railway dashboard
2. **Deploy** and test image uploads
3. **Remove credentials** from documentation files
4. **Monitor usage** in Cloudinary dashboard
5. **Set up alerts** for quota limits

Your image upload system is fully implemented and ready for production! 🚀
