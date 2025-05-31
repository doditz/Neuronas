"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import json
import os
import requests
from flask import Blueprint, redirect, request, url_for, flash, session, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse

# OAuth2 Configuration for Google
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the redirect domain from environment
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")
if REPLIT_DOMAIN.startswith("http"):
    REDIRECT_URL = f"{REPLIT_DOMAIN}/auth/google_callback"
else:
    REDIRECT_URL = f"https://{REPLIT_DOMAIN}/auth/google_callback"

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# OAuth2 Client
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

def is_safe_url(target):
    """
    Check if a URL is safe for redirect (internal to the application).
    Returns True if the URL is safe, False otherwise.
    """
    if not target:
        return False
    
    parsed_url = urlparse(target)
    
    # Allow only relative URLs (no scheme or netloc)
    if parsed_url.netloc or parsed_url.scheme:
        return False
    
    # Must start with '/' to be a valid internal path
    return target.startswith('/')

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/old_login', methods=['GET', 'POST'])
def old_login():
    if request.method == 'POST':
        # Handle traditional email/password login
        email = request.form.get('email')
        password = request.form.get('password')
        remember_value = request.form.get('remember', '')
        remember = remember_value.lower() not in ('', 'false', '0', 'nan') and remember_value
        
        if not email or not password:
            flash("Please enter both email and password", "error")
            return render_template('auth/login.html')
        
        from models import User, db
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect to next page or dashboard (with security validation)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            flash("Invalid email or password", "error")
    
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('auth/signup.html')
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template('auth/signup.html')
        
        from models import User, db
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return render_template('auth/signup.html')
        
        if User.query.filter_by(username=username).first():
            flash("Username already taken", "error")
            return render_template('auth/signup.html')
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        user.created_at = datetime.utcnow()
        user.last_login = datetime.utcnow()
        
        try:
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash(f"Welcome to NeuronasX, {user.username}!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash("Error creating account. Please try again.", "error")
    
    return render_template('auth/signup.html')

@auth_bp.route('/google_login')
def google_login():
    if not GOOGLE_CLIENT_ID:
        flash("Google OAuth is not configured. Please contact support.", "warning")
        return redirect(url_for('auth.login'))
    
    try:
        # Get Google's OpenID configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Prepare authorization request
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=REDIRECT_URL,
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as e:
        flash("Error connecting to Google. Please try again.", "error")
        return redirect(url_for('auth.login'))

@auth_bp.route('/google_callback')
def google_callback():
    if not GOOGLE_CLIENT_ID:
        flash("Google OAuth is not configured", "warning")
        return redirect(url_for('auth.login'))
    
    try:
        # Get authorization code
        code = request.args.get("code")
        if not code:
            flash("Authorization failed", "error")
            return redirect(url_for('auth.login'))
            
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare token exchange request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=REDIRECT_URL,
            code=code,
        )
        
        # Exchange code for token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        if token_response.status_code != 200:
            flash("Failed to authenticate with Google", "error")
            return redirect(url_for('auth.login'))

        # Parse token response
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.status_code != 200:
            flash("Failed to get user information from Google", "error")
            return redirect(url_for('auth.login'))
            
        userinfo = userinfo_response.json()

        # Verify email
        if not userinfo.get("email_verified"):
            flash("Email not verified with Google", "error")
            return redirect(url_for('auth.login'))

        user_email = userinfo["email"]
        user_name = userinfo.get("given_name", user_email.split('@')[0])
        oauth_id = userinfo.get("sub")

        # Find or create user
        from models import User, db
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            # Create new user
            user = User(
                id=str(len(User.query.all()) + 1),  # Simple ID generation
                username=user_name,
                email=user_email,
                oauth_provider="google",
                oauth_id=oauth_id,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
        else:
            # Update OAuth info if needed
            if not user.oauth_provider:
                user.oauth_provider = "google"
                user.oauth_id = oauth_id
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Log in user
        login_user(user)
        flash(f"Welcome, {user.username}!", "success")
        
        # Redirect to intended page or home (with security validation)
        next_page = session.get('next_url')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        else:
            return redirect(url_for('index'))
        
    except Exception as e:
        flash("Authentication error. Please try again.", "error")
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f"Goodbye, {username}!", "info")
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    
    from models import User, db
    
    # Check if username/email already exists (excluding current user)
    if username != current_user.username:
        if User.query.filter_by(username=username).first():
            flash("Username already taken", "error")
            return redirect(url_for('auth.profile'))
    
    if email != current_user.email:
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for('auth.profile'))
    
    # Update user info
    current_user.username = username
    current_user.email = email
    
    try:
        db.session.commit()
        flash("Profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating profile", "error")
    
    return redirect(url_for('auth.profile'))

def init_auth(app):
    """Initialize authentication for the Flask app"""
    from flask_login import LoginManager
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page"
    login_manager.login_message_category = "info"
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return login_manager