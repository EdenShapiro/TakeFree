# 🔐 OAuth Setup Guide

This guide will walk you through setting up social login (Google, Discord, Facebook) for your Props Database.

## 📋 Overview

OAuth allows users to sign in with their existing accounts instead of creating new passwords. It's:
- ✅ **More secure** (no passwords to manage)
- ✅ **Easier for users** (one-click sign-in)
- ✅ **Better privacy** (we never see their password)
- ✅ **Professional** (used by all major apps)

## 🚀 Quick Start (Development)

For local testing, you only need to set up ONE provider. I recommend **Google** (easiest).

### Prerequisites
Your app must be accessible at a consistent URL:
- **Local**: `http://localhost:5001`
- **Production**: `https://your-domain.com`

---

## 🔵 Google OAuth Setup

**Time: ~5 minutes**

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it: "Props Database" 
4. Click "Create"

### Step 2: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (unless you have a Google Workspace)
3. Fill in:
   - **App name**: Props Database
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click "Save and Continue"
5. Skip "Scopes" (click "Save and Continue")
6. Skip "Test users" (unless you want to add specific testers)
7. Click "Back to Dashboard"

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Name it: "Props Database Web"
5. Add **Authorized redirect URIs**:
   - For local: `http://localhost:5001/authorize/google`
   - For production: `https://your-domain.com/authorize/google`
6. Click "Create"
7. **Copy the Client ID and Client Secret** (you'll need these!)

### Step 4: Add to Your App

Create a `.env` file in your project folder:

```bash
cd /Users/edenshapiro/Projects/Stuff
cp .env.example .env
nano .env  # or use any text editor
```

Add your credentials:

```
SECRET_KEY=your-random-secret-key-here
GOOGLE_CLIENT_ID=1234567890-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123xyz
```

**That's it! Google OAuth is ready!** 🎉

---

## 💜 Discord OAuth Setup

**Time: ~3 minutes**

### Step 1: Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it: "Props Database"
4. Accept the terms and click "Create"

### Step 2: Configure OAuth2

1. Click "OAuth2" in the left sidebar
2. Click "Add Redirect"
3. Add redirect URIs:
   - For local: `http://localhost:5001/authorize/discord`
   - For production: `https://your-domain.com/authorize/discord`
4. Click "Save Changes"

### Step 3: Get Your Credentials

1. At the top of the OAuth2 page, you'll see:
   - **Client ID**: Copy this
   - **Client Secret**: Click "Reset Secret" then copy it
2. **Warning**: The secret only shows once! Save it now.

### Step 4: Add to Your App

Add to your `.env` file:

```
DISCORD_CLIENT_ID=1234567890123456789
DISCORD_CLIENT_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

**Discord OAuth is ready!** 🎉

---

## 🔷 Facebook OAuth Setup

**Time: ~5 minutes**

### Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Choose "Consumer" as the app type
4. Click "Next"
5. Fill in:
   - **App name**: Props Database
   - **App contact email**: Your email
6. Click "Create App"

### Step 2: Add Facebook Login

1. In your app dashboard, find "Facebook Login"
2. Click "Set Up"
3. Choose "Web"
4. Enter your site URL:
   - For local: `http://localhost:5001`
   - For production: `https://your-domain.com`
5. Click "Save" and "Continue"

### Step 3: Configure OAuth Redirect URIs

1. Go to "Facebook Login" → "Settings" in the left sidebar
2. Add **Valid OAuth Redirect URIs**:
   - For local: `http://localhost:5001/authorize/facebook`
   - For production: `https://your-domain.com/authorize/facebook`
3. Click "Save Changes"

### Step 4: Get Your Credentials

1. Go to "Settings" → "Basic" in the left sidebar
2. Copy:
   - **App ID**: This is your Client ID
   - **App Secret**: Click "Show" then copy it
3. Scroll down and add your **Privacy Policy URL** (required)
   - For testing: Use any placeholder URL like `https://example.com/privacy`

### Step 5: Make App Public (Optional)

By default, your app is in "Development Mode" - only you can use it.

To allow everyone:
1. Toggle the switch at the top from "In development" to "Live"
2. Choose a category (e.g., "Entertainment")
3. Confirm

### Step 6: Add to Your App

Add to your `.env` file:

```
FACEBOOK_CLIENT_ID=123456789012345
FACEBOOK_CLIENT_SECRET=abcdef0123456789abcdef0123456789
```

**Facebook OAuth is ready!** 🎉

---

## 🔧 Testing Your OAuth Setup

### 1. Install New Dependencies

```bash
cd /Users/edenshapiro/Projects/Stuff
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Your Server

```bash
python app.py
```

### 3. Test Sign-In

1. Open http://localhost:5001
2. Click on one of the OAuth buttons (Google, Discord, or Facebook)
3. You'll be redirected to sign in with that service
4. After signing in, you'll be redirected back to your app
5. You should be logged in! 🎉

---

## 🌐 Production Deployment

When deploying to Railway, Render, or another host:

### 1. Update Redirect URIs

Go back to each OAuth provider and add your production URL:
- Google: Add `https://your-domain.com/authorize/google`
- Discord: Add `https://your-domain.com/authorize/discord`
- Facebook: Add `https://your-domain.com/authorize/facebook`

### 2. Set Environment Variables

In your hosting platform (Railway/Render/etc):
1. Go to your app settings
2. Add environment variables:
   - `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `GOOGLE_CLIENT_ID` - From Google Console
   - `GOOGLE_CLIENT_SECRET` - From Google Console
   - `DISCORD_CLIENT_ID` - From Discord Portal
   - `DISCORD_CLIENT_SECRET` - From Discord Portal
   - `FACEBOOK_CLIENT_ID` - From Facebook Developers
   - `FACEBOOK_CLIENT_SECRET` - From Facebook Developers

### 3. Deploy!

Your OAuth will work automatically once deployed.

---

## 🔒 Security Best Practices

### ✅ Do This:
- ✅ Keep your Client Secrets **private** (never commit to Git)
- ✅ Use HTTPS in production (HTTP only for local testing)
- ✅ Regenerate secrets if they're ever exposed
- ✅ Only add redirect URIs you actually use
- ✅ Use a strong SECRET_KEY

### ❌ Don't Do This:
- ❌ Don't share your `.env` file
- ❌ Don't commit secrets to GitHub
- ❌ Don't use HTTP in production
- ❌ Don't add wildcard redirect URIs (`*`)

---

## 🐛 Troubleshooting

### "Redirect URI mismatch"
**Problem**: The redirect URI doesn't match what's configured.

**Solution**: 
1. Check the URL in your browser when the error happens
2. Make sure it EXACTLY matches what's in your OAuth provider settings
3. Include the protocol (`http://` or `https://`)
4. Check for trailing slashes

### "Client ID not found"
**Problem**: Your credentials aren't being read.

**Solution**:
1. Make sure `.env` file exists in your project root
2. Check that variable names match exactly (case-sensitive)
3. Restart your Flask app after changing `.env`
4. Make sure you ran `pip install python-dotenv`

### "Token validation failed"
**Problem**: Time sync issue or secret mismatch.

**Solution**:
1. Make sure your system clock is correct
2. Verify you copied the Client Secret correctly
3. Try regenerating the secret and updating your `.env`

### Users can't sign in (Facebook)
**Problem**: App is in Development Mode.

**Solution**:
1. Switch app to "Live" mode in Facebook settings
2. Or add specific testers in "Roles" → "Test Users"

### "This app hasn't been verified"
**Problem**: Google shows a warning screen.

**Solution**:
- For testing: Click "Advanced" → "Go to Props Database (unsafe)"
- For production: Submit your app for verification (only needed if you have 100+ users)

---

## 🎯 Which Provider Should I Use?

**For theater/art communities**:
- ✅ **Google** - Most universal, everyone has Gmail
- ✅ **Discord** - Great if your team already uses Discord
- ⚠️ **Facebook** - Many artists avoid Facebook

**Recommendation**: Set up **Google first**, then add others based on your team's preferences.

You can enable all three and let users choose!

---

## 📚 Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Discord OAuth Documentation](https://discord.com/developers/docs/topics/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)

---

## ❓ Need Help?

Common questions:

**Q: Do I need all three providers?**
A: No! Just set up one (Google recommended). Users can only use the providers you configure.

**Q: Can I add more providers later?**
A: Yes! Just follow the setup for each provider and users can use any of them.

**Q: What if I don't want to set this up?**
A: OAuth is required for security. If you prefer, I can add a simple password system back, but OAuth is more secure and easier to maintain.

**Q: How much does this cost?**
A: Free! All three providers offer free OAuth for apps like this.

---

**Ready to test? Set up at least one provider and try signing in!** 🚀
