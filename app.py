from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
import sqlite3
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from uuid import uuid4

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:
    psycopg = None
    dict_row = None

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
if os.environ.get('SESSION_COOKIE_SECURE', '').lower() == 'true':
    app.config['SESSION_COOKIE_SECURE'] = True
DATABASE = os.environ.get('DATABASE_URL', 'props_database.db')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def _is_postgres_url(url):
    return url.startswith('postgres://') or url.startswith('postgresql://')

IS_POSTGRES = _is_postgres_url(DATABASE)
if IS_POSTGRES and psycopg is None:
    raise RuntimeError('PostgreSQL DATABASE_URL set but psycopg is not installed.')

def _translate_sql(sql):
    if IS_POSTGRES:
        return sql.replace('?', '%s')
    return sql

class DB:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=None):
        if params is None:
            params = ()
        cursor = self.conn.cursor()
        cursor.execute(_translate_sql(sql), params)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

# OAuth Configuration
oauth = OAuth(app)

# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Discord OAuth
discord = oauth.register(
    name='discord',
    client_id=os.environ.get('DISCORD_CLIENT_ID'),
    client_secret=os.environ.get('DISCORD_CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify email'}
)

# Facebook OAuth
facebook = oauth.register(
    name='facebook',
    client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
    client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email public_profile'}
)

# Create uploads directory if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def get_db():
    """Create a database connection"""
    if IS_POSTGRES:
        conn = psycopg.connect(DATABASE, row_factory=dict_row)
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
    return DB(conn)

def init_db():
    """Initialize the database with the required schema"""
    db = get_db()
    
    # Create users table with OAuth fields
    if IS_POSTGRES:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                oauth_provider TEXT NOT NULL,
                oauth_id TEXT NOT NULL,
                email TEXT NOT NULL,
                full_name TEXT NOT NULL,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(oauth_provider, oauth_id)
            )
        ''')
    else:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oauth_provider TEXT NOT NULL,
                oauth_id TEXT NOT NULL,
                email TEXT NOT NULL,
                full_name TEXT NOT NULL,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(oauth_provider, oauth_id)
            )
        ''')
    
    # Create items table with user relationship
    if IS_POSTGRES:
        db.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                location TEXT NOT NULL,
                image_path TEXT,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    else:
        db.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                location TEXT NOT NULL,
                image_path TEXT,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
    db.commit()
    db.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token

def csrf_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            session_token = session.get('csrf_token')
            request_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not session_token or not request_token or not secrets.compare_digest(session_token, request_token):
                return jsonify({'error': 'CSRF token missing or invalid'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_or_create_user(oauth_provider, oauth_id, email, full_name, avatar_url=None):
    """Get existing user or create new one from OAuth data"""
    db = get_db()
    
    # Try to find existing user
    user = db.execute(
        'SELECT * FROM users WHERE oauth_provider = ? AND oauth_id = ?',
        (oauth_provider, oauth_id)
    ).fetchone()
    
    if user:
        # Update user info in case it changed
        db.execute(
            '''UPDATE users SET email = ?, full_name = ?, avatar_url = ?
               WHERE id = ?''',
            (email, full_name, avatar_url, user['id'])
        )
        db.commit()
        user_id = user['id']
    else:
        # Create new user
        if IS_POSTGRES:
            cursor = db.execute(
                '''INSERT INTO users (oauth_provider, oauth_id, email, full_name, avatar_url)
                   VALUES (?, ?, ?, ?, ?) RETURNING id''',
                (oauth_provider, oauth_id, email, full_name, avatar_url)
            )
            user_id = cursor.fetchone()['id']
        else:
            cursor = db.execute(
                '''INSERT INTO users (oauth_provider, oauth_id, email, full_name, avatar_url)
                   VALUES (?, ?, ?, ?, ?)''',
                (oauth_provider, oauth_id, email, full_name, avatar_url)
            )
            user_id = cursor.lastrowid
        db.commit()
    
    db.close()
    return user_id

# ============= Authentication Routes =============

@app.route('/')
def index():
    """Serve the main page for all users"""
    logged_in = 'user_id' in session
    csrf_token = get_csrf_token() if logged_in else ''
    return render_template('index.html', csrf_token=csrf_token, logged_in=logged_in)

@app.route('/login/<provider>')
def login(provider):
    """Initiate OAuth login with provider"""
    if provider not in ['google', 'discord', 'facebook']:
        return 'Invalid provider', 400
    
    oauth_client = oauth.create_client(provider)
    redirect_uri = url_for('authorize', provider=provider, _external=True)
    return oauth_client.authorize_redirect(redirect_uri)

@app.route('/authorize/<provider>')
def authorize(provider):
    """Handle OAuth callback"""
    try:
        oauth_client = oauth.create_client(provider)
        token = oauth_client.authorize_access_token()
        
        # Get user info based on provider
        if provider == 'google':
            user_info = token.get('userinfo')
            oauth_id = user_info['sub']
            email = user_info['email']
            full_name = user_info.get('name', email.split('@')[0])
            avatar_url = user_info.get('picture')
            
        elif provider == 'discord':
            resp = oauth_client.get('users/@me')
            user_info = resp.json()
            oauth_id = user_info['id']
            email = user_info.get('email', f"{user_info['username']}@discord.user")
            full_name = user_info.get('global_name') or user_info['username']
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png" if user_info.get('avatar') else None
            
        elif provider == 'facebook':
            resp = oauth_client.get('me?fields=id,name,email,picture')
            user_info = resp.json()
            oauth_id = user_info['id']
            email = user_info.get('email', f"{user_info['id']}@facebook.user")
            full_name = user_info['name']
            avatar_url = user_info.get('picture', {}).get('data', {}).get('url')
        
        # Create or get user
        user_id = get_or_create_user(provider, oauth_id, email, full_name, avatar_url)
        
        # Set session
        session['user_id'] = user_id
        session['full_name'] = full_name
        session['avatar_url'] = avatar_url
        session.permanent = True
        
        return redirect('/')
        
    except Exception as e:
        print(f"OAuth error: {e}")
        return f'Login failed: {str(e)}', 400

@app.route('/api/logout', methods=['POST'])
@csrf_required
def logout():
    """Log out a user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/current-user', methods=['GET'])
def current_user():
    """Get current logged in user info (or null if anonymous)"""
    if 'user_id' not in session:
        return jsonify({'user': None}), 200
    db = get_db()
    user = db.execute('SELECT id, email, full_name, avatar_url, oauth_provider FROM users WHERE id = ?', 
                     (session['user_id'],)).fetchone()
    db.close()
    
    if not user:
        return jsonify({'user': None}), 200
    
    return jsonify({
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'avatar_url': user['avatar_url'],
            'provider': user['oauth_provider']
        }
    }), 200

# ============= Items Routes =============

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items or search items"""
    search_query = request.args.get('search', '').strip()
    
    db = get_db()
    
    if search_query:
        # Search in name, description, owner, and location
        query = '''
            SELECT items.*, users.full_name as owner_name, users.email as owner_contact,
                   users.avatar_url as owner_avatar
            FROM items 
            JOIN users ON items.user_id = users.id
            WHERE items.name LIKE ? OR items.description LIKE ? OR users.full_name LIKE ? OR items.location LIKE ?
            ORDER BY items.created_at DESC
        '''
        search_pattern = f'%{search_query}%'
        items = db.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern)).fetchall()
    else:
        items = db.execute('''
            SELECT items.*, users.full_name as owner_name, users.email as owner_contact,
                   users.avatar_url as owner_avatar
            FROM items 
            JOIN users ON items.user_id = users.id
            ORDER BY items.created_at DESC
        ''').fetchall()
    
    db.close()
    
    # Convert to list of dicts
    items_list = []
    for item in items:
        items_list.append({
            'id': item['id'],
            'name': item['name'],
            'description': item['description'],
            'location': item['location'],
            'image_path': item['image_path'],
            'owner_name': item['owner_name'],
            'owner_contact': item['owner_contact'],
            'owner_avatar': item['owner_avatar'],
            'user_id': item['user_id'],
            'is_owner': ('user_id' in session and item['user_id'] == session['user_id']),
            'created_at': item['created_at'],
            'updated_at': item['updated_at']
        })
    
    return jsonify(items_list)

@app.route('/api/items', methods=['POST'])
@login_required
@csrf_required
def add_item():
    """Add a new item to the database"""
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        
        # Validate required fields
        if not name:
            return jsonify({'error': 'Item name is required'}), 400
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = secure_filename(file.filename)
                extension = Path(safe_name).suffix.lower()
                filename = f"{timestamp}_{uuid4().hex}{extension}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = filename
        
        # Insert into database
        db = get_db()
        if IS_POSTGRES:
            cursor = db.execute(
                '''INSERT INTO items (name, description, location, image_path, user_id)
                   VALUES (?, ?, ?, ?, ?) RETURNING id''',
                (name, description, location, image_path, session['user_id'])
            )
            item_id = cursor.fetchone()['id']
        else:
            cursor = db.execute(
                '''INSERT INTO items (name, description, location, image_path, user_id)
                   VALUES (?, ?, ?, ?, ?)''',
                (name, description, location, image_path, session['user_id'])
            )
            item_id = cursor.lastrowid
        db.commit()
        db.close()
        
        return jsonify({
            'message': 'Item added successfully',
            'id': item_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
@csrf_required
def update_item(item_id):
    """Update an existing item in the database"""
    try:
        db = get_db()
        
        # Check if item exists and user owns it
        item = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        if not item:
            db.close()
            return jsonify({'error': 'Item not found'}), 404
        
        if item['user_id'] != session['user_id']:
            db.close()
            return jsonify({'error': 'You can only edit your own items'}), 403
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        
        # Validate required fields
        if not name:
            return jsonify({'error': 'Item name is required'}), 400
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Handle image upload
        image_path = item['image_path']  # Keep existing image by default
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if it exists
                if item['image_path']:
                    old_image_path = os.path.join(UPLOAD_FOLDER, item['image_path'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = secure_filename(file.filename)
                extension = Path(safe_name).suffix.lower()
                filename = f"{timestamp}_{uuid4().hex}{extension}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = filename
        
        # Update database
        db.execute(
            '''UPDATE items 
               SET name = ?, description = ?, location = ?, image_path = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (name, description, location, image_path, item_id)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'message': 'Item updated successfully',
            'id': item_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
@csrf_required
def delete_item(item_id):
    """Delete an item from the database"""
    try:
        db = get_db()
        
        # Get the item and check ownership
        item = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        
        if not item:
            db.close()
            return jsonify({'error': 'Item not found'}), 404
        
        if item['user_id'] != session['user_id']:
            db.close()
            return jsonify({'error': 'You can only delete your own items'}), 403
        
        # Delete the image file if it exists
        if item['image_path']:
            image_path = os.path.join(UPLOAD_FOLDER, item['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete from database
        db.execute('DELETE FROM items WHERE id = ?', (item_id,))
        db.commit()
        db.close()
        
        return jsonify({'message': 'Item deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(UPLOAD_FOLDER, filename)

cors_origins = [o.strip() for o in os.environ.get('CORS_ORIGINS', '').split(',') if o.strip()]
if cors_origins:
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": cors_origins}})

# Initialize database on startup for WSGI servers
init_db()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Props Database Server Starting!")
    print("="*50)
    print("\nAccess the application at: http://localhost:5001")
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
