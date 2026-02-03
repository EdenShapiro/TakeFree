# 🚀 Deployment Guide - Props Database

This guide will help you deploy your Props Database to the internet so your team can access it from anywhere.

## 🎯 Deployment Options

### Option 1: Railway.app (Recommended - Easiest)

**Railway** is perfect for beginners and has a generous free tier.

#### Steps:

1. **Create a GitHub account** (if you don't have one)
   - Go to https://github.com and sign up

2. **Upload your code to GitHub**
   ```bash
   cd /Users/edenshapiro/Projects/Stuff
   git init
   git add .
   git commit -m "Initial commit - Props Database"
   
   # Create a new repository on GitHub, then:
   git remote add origin https://github.com/YOUR-USERNAME/props-database.git
   git push -u origin main
   ```

3. **Sign up for Railway**
   - Go to https://railway.app
   - Click "Login" and use your GitHub account
   
4. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `props-database` repository
   - Railway will automatically detect it's a Python app
   
5. **Add Environment Variables**
   - Click on your deployed service
   - Go to "Variables" tab
   - Add:
     ```
     SECRET_KEY = (click "Generate" for a random secret)
     ```
   
6. **Get your URL**
   - Go to "Settings" tab
   - Click "Generate Domain"
   - Your app will be live at: `https://your-app-name.up.railway.app`

**Cost**: Free for small projects (500 hours/month, ~$5 credit)

---

### Option 2: Render.com (Good Alternative)

**Render** is also beginner-friendly with a solid free tier.

#### Steps:

1. **Upload to GitHub** (same as Railway steps 1-2)

2. **Sign up for Render**
   - Go to https://render.com
   - Click "Get Started" and use GitHub

3. **Create a Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `props-database`
   
4. **Configure the Service**
   - Name: `props-database`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   
5. **Add Environment Variable**
   - Scroll down to "Environment Variables"
   - Add:
     ```
     SECRET_KEY = (generate a random string)
     ```
   
6. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your URL: `https://props-database.onrender.com`

**Cost**: Free tier available (sleeps after inactivity, wakes up when accessed)

---

### Option 3: PythonAnywhere (Python-Specific)

**PythonAnywhere** is designed specifically for Python apps.

#### Steps:

1. **Sign up**
   - Go to https://www.pythonanywhere.com
   - Create a free "Beginner" account
   
2. **Upload Files**
   - Go to "Files" tab
   - Click "Upload a file" or use Git to clone
   
3. **Create Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask"
   - Python version: 3.11
   
4. **Configure**
   - Set working directory: `/home/yourusername/props-database`
   - Edit WSGI file to point to your `app.py`
   - Set environment variables in "Environment" section
   
5. **Reload**
   - Click "Reload" button
   - Your URL: `https://yourusername.pythonanywhere.com`

**Cost**: Free tier available (limited to 1 web app)

---

### Option 4: Local Network Only (No Internet)

If you only need access within your office/home:

1. **Find your computer's IP address**
   - Mac: System Preferences → Network
   - Windows: Run `ipconfig` in Command Prompt
   - Linux: Run `ip addr` or `ifconfig`
   
2. **Start the server**
   ```bash
   python app.py
   ```
   
3. **Share the URL**
   - Give your team: `http://YOUR-IP-ADDRESS:5001`
   - Example: `http://192.168.1.100:5001`
   
4. **Keep it running**
   - Your computer must stay on
   - Everyone must be on the same WiFi/network

**Cost**: Free! No hosting needed

---

## 🔒 Security Checklist

Before going live, make sure you've done these:

### ✅ Essential Security

- [ ] **Change SECRET_KEY** - Never use the default! Generate a random one
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] **Use HTTPS** - Railway, Render, and PythonAnywhere provide this automatically

- [ ] **Set strong passwords** - Tell users to create passwords with 8+ characters

- [ ] **Backup your database** - Download `props_database.db` regularly

### ✅ Recommended Security (Future)

- [ ] Email verification for new accounts
- [ ] Password reset functionality  
- [ ] Two-factor authentication
- [ ] Admin role to manage users
- [ ] Rate limiting to prevent abuse
- [ ] CSRF token protection

---

## 📊 Using PostgreSQL (Production Database)

SQLite is great for development, but for production with multiple users, use PostgreSQL:

### Railway/Render (Automatic)

Both platforms can add PostgreSQL automatically:

1. **Railway**: Click "+ New" → "Database" → "PostgreSQL"
2. **Render**: It's configured in `render.yaml` (already done!)

Your app will automatically detect the PostgreSQL connection string.

### Manual PostgreSQL Setup

If you need to set it up manually:

1. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

2. Add to `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```

3. Set `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

4. Update `app.py` to use PostgreSQL (current code already supports this!)

---

## 🧪 Testing Your Deployment

After deploying:

1. **Visit your URL** - Make sure the login page loads
2. **Create an account** - Register a new user
3. **Add an item** - Test creating items with photos
4. **Search** - Try searching for items
5. **Edit/Delete** - Test editing your own items
6. **Invite a friend** - Have someone else register and test

---

## 🐛 Troubleshooting

### App won't start
- Check logs on your hosting platform
- Verify all environment variables are set
- Make sure `requirements.txt` is correct

### Images not uploading
- Check file size limits (most platforms: 10-50MB)
- Verify `uploads/` directory exists
- For production, consider cloud storage (AWS S3, Cloudinary)

### Database errors
- Make sure database is connected
- Check DATABASE_URL is correct
- Try resetting database (delete and recreate)

### Can't log in
- Clear browser cookies
- Check SECRET_KEY is set
- Verify database has users table

---

## 💾 Backup & Maintenance

### Regular Backups

Download your database regularly:

1. **Local**: Copy `props_database.db`
2. **Railway**: Use Railway's backup feature
3. **Render**: Export from PostgreSQL dashboard

### Updating the Code

1. Make changes locally
2. Test thoroughly
3. Push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
4. Railway/Render will auto-deploy

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (if needed) | Best For |
|----------|-----------|------------------|----------|
| **Railway** | $5 credit/month | ~$5-20/month | Easiest setup |
| **Render** | Free (sleeps) | $7/month | Good balance |
| **PythonAnywhere** | 1 app free | $5/month | Python focus |
| **DigitalOcean** | None | $5/month | More control |
| **Local Network** | Free | Free | In-office only |

---

## 🎓 Next Steps

After deployment:

1. **Share the URL** with your team
2. **Create admin account** first
3. **Set guidelines** for item descriptions
4. **Train users** on how to use it
5. **Collect feedback** and improve

---

## 📞 Need Help?

- Check logs on your hosting platform
- Search error messages on Google/Stack Overflow
- Review Flask documentation: https://flask.palletsprojects.com
- Railway docs: https://docs.railway.app
- Render docs: https://render.com/docs

Good luck with your deployment! 🚀
