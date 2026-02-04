# 🎭 Props & Items Database

A secure, web-based database system for tracking props, costumes, set pieces, and items across your interactive art organization. Never buy duplicate props again when someone in your organization already owns what you need!

## ✨ Features

### Core Features
- 🔐 **User Authentication**: Secure login and registration system
- ✨ **Simple Item Entry**: Add items with name, description, location, and photo
- 🔍 **Powerful Search**: Search by item name, description, owner, or location
- 📸 **Image Upload**: Upload photos or paste directly from clipboard
- 👤 **Owner Tracking**: Automatically tracks who owns each item
- 📍 **Location Tracking**: Know where items are stored
- ✏️ **Edit Your Items**: Update or delete items you've added
- 🎨 **Beautiful UI**: Modern, responsive design that works on all devices

### Security Features
- 🔐 **OAuth Social Login**: Sign in with Google, Discord, or Facebook
- 👥 **No Passwords to Manage**: More secure than traditional passwords
- 🛡️ **Ownership Control**: Users can only edit/delete their own items
- 🔑 **Session Management**: Secure, persistent login sessions
- 🌐 **Production Ready**: Configured for secure deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory**:
```bash
cd /Users/edenshapiro/Projects/Stuff
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up OAuth** (Required for login):
   - See **[OAUTH_SETUP.md](OAUTH_SETUP.md)** for detailed instructions
   - Quick start: Set up Google OAuth (takes 5 minutes)
   - Create `.env` file with your OAuth credentials

5. **Run the application**:
```bash
python app.py
```

6. **Open your browser** and go to:
```
http://localhost:5001
```

7. **Sign in** with Google/Discord/Facebook and start adding items!

## 📖 Usage Guide

### First Time Setup

1. **Sign In with OAuth**
   - Choose Google, Discord, or Facebook
   - Click the button to sign in
   - Approve the permissions
   - You're automatically logged in!

2. **No passwords needed!** Your account is linked to your Google/Discord/Facebook identity

### Adding Items

1. Use the form on the left side
2. Required fields:
   - **Item Name**: What is it?
   - **Location**: Where is it stored?
3. Optional fields:
   - **Description**: Details, condition, special features
   - **Photo**: Upload or paste an image (Cmd/Ctrl+V)
4. Click "Add Item"

### Searching for Items

- Use the search bar to find items
- Search works across names, descriptions, owners, and locations
- Results update as you type
- See who owns each item and where it's located

### Managing Your Items

- **Edit**: Click the blue "Edit" button on items you own
- **Delete**: Click the red "Delete" button on items you own
- **View Others**: See all items in the database (read-only for items you don't own)

### Pasting Images

You can paste images directly from your clipboard:
1. Copy any image (screenshot, right-click → copy, etc.)
2. Press **Cmd+V** (Mac) or **Ctrl+V** (Windows/Linux) anywhere on the page
3. The image will automatically appear in the form!

## 🌐 Deployment

Want to make this accessible to your team online? See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed guides on:

- **Railway.app** (Recommended - easiest)
- **Render.com** (Great free tier)
- **PythonAnywhere** (Python-specific hosting)
- **Local Network** (Office/home only, free)

## 🔒 Security

This application includes production-grade security:

✅ **OAuth 2.0 authentication** (Google, Discord, Facebook)  
✅ **No password storage** (more secure than traditional passwords)  
✅ **Session-based authentication**  
✅ **Ownership verification** (users can only edit their own items)  
✅ **SQL injection protection** (parameterized queries)  
✅ **XSS protection** (HTML escaping)  
✅ **Environment variable configuration**  
✅ **HTTPS ready** for deployment

## 🧰 Stack & Hosting

- **Backend**: Python + Flask
- **Frontend**: HTML/CSS + vanilla JS (server-rendered templates)
- **Auth**: OAuth via Authlib (Google; Discord/Facebook optional)
- **Database**: Neon Postgres (production), SQLite (local dev)
- **Hosting**: Render (web service)
- **Image Storage**: Cloudinary
- **Domain/DNS**: Cloudflare

### Security Best Practices

When deploying to production:

1. **Set up OAuth credentials** for at least one provider
   - See [OAUTH_SETUP.md](OAUTH_SETUP.md) for step-by-step instructions
   - Google is recommended (easiest and most universal)

2. **Set a strong SECRET_KEY** (never use the default!)
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Use HTTPS** (automatic on Railway/Render/PythonAnywhere)

4. **Keep OAuth secrets private** (never commit `.env` to Git)

5. **Backup your database** regularly

## 📁 Project Structure

```
Stuff/
├── app.py                  # Flask backend with authentication
├── templates/
│   ├── index.html         # Main app interface (logged in users)
│   └── login.html         # Login/registration page
├── uploads/               # Uploaded images (auto-created)
├── props_database.db      # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration (Railway/Render)
├── runtime.txt           # Python version for deployment
├── railway.json          # Railway-specific config
├── render.yaml           # Render-specific config
├── .env.example          # Example environment variables
├── DEPLOYMENT.md         # Deployment guide
└── README.md             # This file
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    oauth_provider TEXT NOT NULL,
    oauth_id TEXT NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMP,
    UNIQUE(oauth_provider, oauth_id)
);
```

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT NOT NULL,
    image_path TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔧 Technical Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Development database
- **Authlib** - OAuth 2.0 authentication
- **Sessions** - User authentication

### Frontend
- **HTML/CSS/JavaScript** - No frameworks needed!
- **Responsive design** - Works on phones, tablets, desktops
- **Modern UI** - Gradient backgrounds, smooth animations

### Deployment
- **Gunicorn** - Production WSGI server
- **PostgreSQL ready** - For production deployments
- **Railway/Render/PythonAnywhere** - Easy hosting options

## 📊 API Endpoints

### Authentication
- `GET /login/<provider>` - Initiate OAuth login (google/discord/facebook)
- `GET /authorize/<provider>` - OAuth callback handler
- `POST /api/logout` - Log out
- `GET /api/current-user` - Get logged-in user info

### Items
- `GET /api/items` - Get all items (with search)
- `POST /api/items` - Add new item (requires login)
- `PUT /api/items/<id>` - Update item (owner only)
- `DELETE /api/items/<id>` - Delete item (owner only)

## 🎯 Use Cases

Perfect for:
- 🎭 **Theatre companies** - Track costumes, props, set pieces
- 🎬 **Film productions** - Share equipment and props
- 🎨 **Art collectives** - Organize shared materials
- 🎪 **Event organizers** - Manage decorations and supplies
- 📚 **Maker spaces** - Track tools and materials
- 🏢 **Any organization** with shared physical items

## 🔄 Updating the Application

To update after making changes:

```bash
# Pull latest changes
git pull

# Restart the server
# (If deployed, push to GitHub and platform will auto-deploy)
git add .
git commit -m "Your changes"
git push
```

## 💾 Backup

### Local Backup
Simply copy the database file:
```bash
cp props_database.db props_database_backup_$(date +%Y%m%d).db
```

### Production Backup
- **Railway**: Use built-in backup tools
- **Render**: PostgreSQL automatic backups
- **PythonAnywhere**: Download from Files tab

## 🐛 Troubleshooting

### Port 5000 already in use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5002)  # Use any available port
```

### Can't log in
- Make sure OAuth is configured (check `.env` file)
- Verify redirect URIs match in OAuth provider settings
- Clear your browser cookies
- Check console/logs for error messages

### Images not uploading
- Check `uploads/` directory exists
- Verify supported formats: PNG, JPG, JPEG, GIF, WEBP
- Check file size (default limit: 16MB)

### Database errors
Delete and recreate:
```bash
rm props_database.db
python app.py  # Will recreate automatically
```

## 🚧 Future Enhancements

Possible features to add:
- [ ] Email verification
- [ ] Password reset via email
- [ ] Admin dashboard
- [ ] Item categories/tags
- [ ] Advanced filtering
- [ ] Item reservation system
- [ ] Multiple photos per item
- [ ] Item history/changelog
- [ ] Export to CSV/PDF
- [ ] Cloud storage for images (AWS S3)
- [ ] Mobile app

## 📝 License

Created for internal use by your interactive art organization. Modify and distribute as needed!

## 🤝 Contributing

Want to improve this? 
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📞 Support

- Check logs for error messages
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Search error messages online
- Flask docs: https://flask.palletsprojects.com

---

**Built with ❤️ for creative communities**
