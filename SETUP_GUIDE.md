# Complete Facebook App Setup Guide

## Problem: Can't See Ads Permissions in Graph API Explorer

If you only see `public_profile` permission, your app needs Marketing API enabled.

## Solution: Enable Marketing API

### Step 1: Go to Your Facebook App
1. Visit https://developers.facebook.com/apps
2. Select your app (ID: 972844235010467 or your app)

### Step 2: Add Marketing API Product
1. In the left sidebar, click **"Add Product"** or **"Products"**
2. Find **"Marketing API"** in the product list
3. Click **"Set Up"** or **"Add"** button
4. Accept the terms if prompted

### Step 3: Configure Marketing API
1. After adding, click **"Marketing API"** in the left sidebar
2. Go to **"Tools"** section
3. You should see options for:
   - Ad Account Selection
   - Token Generation
   - API Settings

### Step 4: Add Yourself as a Test User (Important!)
1. In left sidebar, go to **"Roles" → "Roles"**
2. Under **"Test Users"** or **"Developers"**, add your Facebook account
3. Or go to **"Test Users"** and create/add test users

### Step 5: Link Your Ad Account (If you have one)
1. Go to **"Marketing API" → "Tools"**
2. Click **"Add Ad Accounts"**
3. Link your Business Manager ad accounts
4. This allows the app to access your ad data

### Step 6: Try Graph API Explorer Again
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click **"Permissions"** or **"Generate Access Token"**
4. You should now see:
   - ✓ ads_read
   - ✓ ads_management
   - ✓ business_management
   - ✓ read_insights

## Alternative: Create App from Business Manager (Better Approach)

If above doesn't work, create app through Business Manager:

### Method 2: Create App via Business Manager

1. **Go to Business Settings**
   - Visit https://business.facebook.com/settings
   - Select your Business Manager

2. **Create System User (Recommended for Production)**
   - Go to **"Users" → "System Users"**
   - Click **"Add"**
   - Give it Admin role
   - Click **"Generate New Token"**
   - Select your ad account
   - Choose permissions:
     - ads_read
     - ads_management
     - business_management
   - Copy the token (this never expires!)

3. **Or Use Business Manager Apps**
   - Go to **"Business Settings" → "Apps"**
   - Add your app
   - Grant it access to your ad accounts
   - This automatically enables Marketing API

## Troubleshooting

### "I still can't see ads permissions"

**Check App Type:**
1. In your app dashboard, check the **"App Type"**
2. It should be **"Business"** type
3. If it's "Consumer" or "Gaming", you may need to create a new Business type app

**Verify App Mode:**
1. Top of your app dashboard shows app mode
2. Should say **"Development Mode"** (green)
3. Development mode allows testing without App Review

**Add Your Ad Account:**
1. You must have a Facebook Ad Account
2. Link it in Business Manager or Marketing API settings
3. Without an ad account, permissions won't appear

### "I have the permissions but token doesn't work"

**Verify Your Identity:**
1. Make sure you're logged into Facebook with the account that:
   - Created the app OR
   - Is added as Admin/Developer/Tester in the app

**Check Ad Account Access:**
1. Your Facebook account must have access to at least one ad account
2. Go to https://business.facebook.com/
3. Verify you can see ad accounts there

## Quick Test

After setup, test your token:

```bash
# Get token from Graph API Explorer with ads permissions
python generate_token.py

# Or test directly
curl "https://graph.facebook.com/v23.0/me/adaccounts?access_token=YOUR_TOKEN"
```

If you see ad accounts, it works! ✅

## For Production Use

For production applications:

1. **Submit for App Review**
   - Required for public use
   - Marketing API permissions need review
   - Process takes 3-7 days

2. **Use System Users** (Business Manager)
   - More reliable than user tokens
   - No expiration
   - Better for server-to-server

3. **Set Up Webhooks** (Optional)
   - Real-time notifications
   - Changes to campaigns, ads, etc.

---

Need help? Check:
- [Marketing API Documentation](https://developers.facebook.com/docs/marketing-apis)
- [App Review Process](https://developers.facebook.com/docs/app-review)
- [System Users Guide](https://www.facebook.com/business/help/503306463479099)
