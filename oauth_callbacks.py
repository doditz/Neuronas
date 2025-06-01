
"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import os
import json
import requests
import jwt
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_user
from oauthlib.oauth2 import WebApplicationClient
from urllib.parse import urlparse

from app import db
from models import User, OAuth

# Create OAuth callbacks blueprint
oauth_callbacks_bp = Blueprint('oauth_callbacks', __name__)

# OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get domain for callbacks
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")
if not REPLIT_DOMAIN.startswith("http"):
    BASE_URL = f"https://{REPLIT_DOMAIN}"
else:
    BASE_URL = REPLIT_DOMAIN

# OAuth2 Client for Google
google_client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

def is_safe_url(target):
    """Check if a URL is safe for redirect"""
    if not target:
        return False
    parsed_url = urlparse(target)
    return not parsed_url.netloc and not parsed_url.scheme and target.startswith('/')

def create_or_update_user(email, username, first_name=None, last_name=None, 
                         oauth_provider=None, oauth_id=None, profile_image_url=None):
    """Create or update user from OAuth data"""
    # Try to find existing user by email or OAuth ID
    user = None
    if oauth_id:
        user = User.query.filter_by(oauth_id=oauth_id, oauth_provider=oauth_provider).first()
    if not user and email:
        user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create new user
        # Make username unique
        base_username = username or email.split('@')[0] if email else f"user_{oauth_id}"
        unique_username = base_username
        counter = 1
        while User.query.filter_by(username=unique_username).first():
            unique_username = f"{base_username}{counter}"
            counter += 1
            
        user = User(
            username=unique_username,
            email=email,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image_url,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
    else:
        # Update existing user
        if not user.oauth_provider and oauth_provider:
            user.oauth_provider = oauth_provider
            user.oauth_id = oauth_id
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_image_url:
            user.profile_image_url = profile_image_url
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    return user

@oauth_callbacks_bp.route('/google/login')
def google_login():
    """Initiate Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET", "error")
        return redirect(url_for('index'))
    
    try:
        # Get Google's OpenID configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Store the next URL in session
        session['oauth_next'] = request.args.get('next')
        
        # Prepare authorization request
        request_uri = google_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=f"{BASE_URL}/auth/google/callback",
            scope=["openid", "email", "profile"],
            state="google"  # Add state for security
        )
        return redirect(request_uri)
    except Exception as e:
        flash(f"Error initiating Google login: {str(e)}", "error")
        return redirect(url_for('index'))

@oauth_callbacks_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google OAuth is not configured", "error")
        return redirect(url_for('index'))
    
    try:
        # Get authorization code
        code = request.args.get("code")
        state = request.args.get("state")
        
        if not code:
            error = request.args.get("error")
            flash(f"Google OAuth error: {error}", "error")
            return redirect(url_for('index'))
        
        # Get Google's configuration
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Exchange code for token
        token_url, headers, body = google_client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=f"{BASE_URL}/auth/google/callback",
            code=code,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        if token_response.status_code != 200:
            flash("Failed to get access token from Google", "error")
            return redirect(url_for('index'))
        
        # Parse token response
        google_client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = google_client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.status_code != 200:
            flash("Failed to get user information from Google", "error")
            return redirect(url_for('index'))
        
        userinfo = userinfo_response.json()
        
        # Verify email
        if not userinfo.get("email_verified"):
            flash("Email not verified with Google", "error")
            return redirect(url_for('index'))
        
        # Create or update user
        user = create_or_update_user(
            email=userinfo["email"],
            username=userinfo.get("given_name", userinfo["email"].split('@')[0]),
            first_name=userinfo.get("given_name"),
            last_name=userinfo.get("family_name"),
            oauth_provider="google",
            oauth_id=userinfo["sub"],
            profile_image_url=userinfo.get("picture")
        )
        
        # Log in user
        login_user(user)
        flash(f"Welcome, {user.username}!", "success")
        
        # Redirect to next page or home
        next_page = session.pop('oauth_next', None)
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for('index'))

@oauth_callbacks_bp.route('/replit/login')
def replit_login():
    """Initiate Replit OAuth flow"""
    repl_id = os.environ.get('REPL_ID')
    if not repl_id:
        flash("Replit OAuth is not available - REPL_ID not set", "error")
        return redirect(url_for('index'))
    
    # Store the next URL in session
    session['oauth_next'] = request.args.get('next')
    
    # Redirect to Replit's OAuth through the existing blueprint
    return redirect('/auth/replit_auth/login')

@oauth_callbacks_bp.route('/replit/callback')
def replit_callback():
    """Handle Replit OAuth callback - this is handled by the existing replit_auth blueprint"""
    # This route exists for completeness but the actual callback is handled 
    # by the replit_auth blueprint
    return redirect(url_for('index'))

@oauth_callbacks_bp.route('/logout')
def logout():
    """Universal logout handler"""
    from flask_login import logout_user, current_user
    
    if current_user.is_authenticated:
        username = current_user.username
        provider = getattr(current_user, 'oauth_provider', None)
        
        # Clear session
        session.clear()
        logout_user()
        
        flash(f"Goodbye, {username}!", "info")
        
        # Redirect to provider-specific logout if needed
        if provider == 'replit':
            return redirect('/auth/replit_auth/logout')
    
    return redirect(url_for('index'))

def init_oauth_callbacks(app):
    """Initialize OAuth callbacks for the Flask app"""
    app.register_blueprint(oauth_callbacks_bp, url_prefix='/auth')
    return oauth_callbacks_bp
