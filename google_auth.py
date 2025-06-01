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
from flask import Blueprint, redirect, request, url_for, flash
from flask_login import login_user
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime

from app import db
from models import User

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the redirect domain from environment
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN")
if REPLIT_DOMAIN:
    DEV_REDIRECT_URL = f'https://{REPLIT_DOMAIN}/auth/google/callback'
else:
    DEV_REDIRECT_URL = 'http://localhost:5000/auth/google/callback'

# Display setup instructions to the user
print(f"""To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs

For detailed instructions, see:
https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client
""")

# OAuth2 Client
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

google_auth = Blueprint("google_auth", __name__)

@google_auth.route("/google/signin")
def google_signin():
    """Start Google OAuth authentication"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google authentication is not configured. Please set up your OAuth credentials.", "warning")
        return redirect(url_for('index'))

    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http://", "https://").replace("/signin", "/callback"),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@google_auth.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google authentication is not configured.", "error")
        return redirect(url_for('index'))

    try:
        code = request.args.get("code")
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace("http://", "https://"),
            redirect_url=request.base_url.replace("http://", "https://"),
            code=code,
        )

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        userinfo = userinfo_response.json()

        if userinfo.get("email_verified"):
            users_email = userinfo["email"]
            users_name = userinfo.get("given_name", userinfo["email"].split('@')[0])
            google_id = userinfo["sub"]
            profile_pic = userinfo.get("picture")
        else:
            flash("User email not available or not verified by Google.", "error")
            return redirect(url_for('index'))

        # Check if user exists by email or Google ID
        user = User.query.filter(
            (User.email == users_email) | (User.oauth_id == google_id)
        ).first()

        if not user:
            # Create new user with Google ID as primary key
            user = User()
            user.id = google_id
            user.username = users_name
            user.email = users_email
            user.oauth_provider = "google"
            user.oauth_id = google_id
            user.first_name = userinfo.get("given_name")
            user.last_name = userinfo.get("family_name")
            user.profile_image_url = profile_pic
            user.created_at = datetime.utcnow()
            user.last_login = datetime.utcnow()

            # Make sure username is unique
            base_username = users_name
            counter = 1
            while User.query.filter_by(username=user.username).first() is not None:
                user.username = f"{base_username}{counter}"
                counter += 1

            db.session.add(user)
        else:
            # Update existing user info
            user.last_login = datetime.utcnow()
            user.first_name = userinfo.get("given_name", user.first_name)
            user.last_name = userinfo.get("family_name", user.last_name)
            user.profile_image_url = profile_pic or user.profile_image_url

        db.session.commit()
        login_user(user)

        flash(f"Welcome to NeuronasX, {user.username}!", "success")
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for('index'))

def create_google_blueprint():
    """Create and return the Google auth blueprint"""
    return google_auth