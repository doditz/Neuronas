"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

import jwt
import os
import uuid
from functools import wraps
from urllib.parse import urlencode

from flask import g, session, redirect, request, render_template, url_for, flash
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

from app import app, db
from models import OAuth, User

login_manager = LoginManager(app)
login_manager.login_view = "replit_auth.signin"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class UserSessionStorage(BaseStorage):
    def get(self, blueprint):
        try:
            token = db.session.query(OAuth).filter_by(
                user_id=current_user.get_id(),
                browser_session_key=g.browser_session_key,
                provider=blueprint.name,
            ).one().token
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name).delete()
        db.session.commit()

def make_replit_blueprint():
    try:
        repl_id = os.environ['REPL_ID']
    except KeyError:
        app.logger.error("REPL_ID environment variable is not set, Replit authentication will not be available")
        return None

    issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if '_browser_session_key' not in session:
            session['_browser_session_key'] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session['_browser_session_key']
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/signin")
    def signin():
        """Start Replit OAuth authentication"""
        # Redirect to Flask-Dance OAuth endpoint
        return redirect(url_for("replit_auth.authorized"))

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id": repl_id,
            "post_logout_redirect_uri": request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        flash("An authentication error occurred", "danger")
        return redirect(url_for('index'))

    return replit_bp

def save_user(user_claims):
    """
    Save or update user from OIDC claims
    """
    user = User.query.filter_by(id=user_claims['sub']).first()
    
    if user is None:
        # Create new user
        user = User()
        user.id = user_claims['sub']
        
        # Generate username from email or user ID
        if user_claims.get('email'):
            username = user_claims['email'].split('@')[0]
        else:
            username = f"user_{user_claims['sub']}"
            
        # Make sure username is unique
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first() is not None:
            username = f"{base_username}{counter}"
            counter += 1
            
        user.username = username
        user.created_at = datetime.utcnow()
    
    # Update user info
    user.email = user_claims.get('email')
    user.first_name = user_claims.get('first_name')
    user.last_name = user_claims.get('last_name')
    user.profile_image_url = user_claims.get('profile_image_url')
    user.oauth_provider = "replit"
    user.oauth_id = user_claims['sub']
    user.last_login = datetime.utcnow()
    
    db.session.add(user)
    db.session.commit()
    return user

@oauth_authorized.connect
def logged_in(blueprint, token):
    if blueprint.name != 'replit_auth':
        return
        
    try:
        if not token:
            flash("Token d'authentification manquant", "danger")
            return redirect(url_for('index'))
            
        # Decode the JWT token without verification first to get user info
        user_claims = jwt.decode(
            token['id_token'],
            options={"verify_signature": False}
        )
        
        # Save user to database
        user = save_user(user_claims)
        login_user(user)
        blueprint.token = token
        
        flash(f"Bienvenue, {user.username}!", "success")
        
        next_url = session.pop("next_url", None)
        if next_url is not None:
            return redirect(next_url)
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Erreur lors de l'authentification Replit: {e}")
        flash("Erreur d'authentification. Veuillez réessayer.", "danger")
        return redirect(url_for('index'))

@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    if blueprint.name != 'replit_auth':
        return
        
    app.logger.error(f"OAuth error with Replit: {error}, {error_description}")
    flash(f"Authentication error: {error_description or error}", "danger")
    return redirect(url_for('index'))

def require_login(f):
    """
    Decorator to require login for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next_url"] = request.url
            return redirect(url_for('replit_auth.login'))

        return f(*args, **kwargs)

    return decorated_function
    
# Import datetime for user creation/update
from datetime import datetime