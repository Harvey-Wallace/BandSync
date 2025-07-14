# Railway Environment Variables for BandSync

## 🚨 **Critical Issue Found: Missing REACT_APP_API_URL**

Your deployed app is failing because the `REACT_APP_API_URL` environment variable is not set in Railway. This causes all API calls to fail.

## 🔧 **Fix Required in Railway Dashboard:**

### **1. Set the API Base URL**
In your Railway dashboard, add this environment variable:

```bash
REACT_APP_API_URL=https://your-app-name.railway.app
```

**Replace `your-app-name` with your actual Railway app domain.**

### **2. Existing Cloudinary Variables** (already working)
```bash
CLOUDINARY_CLOUD_NAME=di0gom1vd
CLOUDINARY_API_KEY=982593917724433
CLOUDINARY_API_SECRET=oGCqi0PHPSR8wOPce5WX1XSoZkY
```

### **3. Other Required Variables**
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://...
```

## 🎯 **How to Find Your Railway App URL:**

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Settings" tab
4. Look for "Domains" section
5. Copy the Railway-provided domain (e.g., `https://bandsync-production.up.railway.app`)
6. Add this as `REACT_APP_API_URL` in the Variables tab

## 🔄 **After Setting the Variable:**

1. Railway will automatically redeploy
2. Your navbar should start working
3. Organization logos and themes will load
4. Profile data will display correctly

## 📝 **Note:**

React environment variables are compiled into the build at build time, so you MUST set `REACT_APP_API_URL` before the build process runs. That's why your local version works (it has a .env file) but Railway doesn't.

## 🧪 **Test After Fix:**

1. Wait for Railway to redeploy
2. Check if organization logo appears
3. Test profile bubble on different pages
4. Verify theme colors load correctly

This should fix all your navbar issues!
