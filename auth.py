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
from flask import Blueprint, redirect, request, url_for, flash, session, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime

# Configuration OAuth2 pour Google
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Get the redirect domain from environment
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")
REDIRECT_URL = f"https://{REPLIT_DOMAIN}/google_login/callback"

# Créer un blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__)

# Client OAuth2
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None)

# Initialiser le client OAuth2
client = WebApplicationClient(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else None

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route('/login')
def login():
    if not GOOGLE_CLIENT_ID:
        flash("Identifiants Google OAuth non configurés", "warning")
        return redirect(url_for('index'))
    
    # Authentification Google
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Préparation de la requête d'autorisation
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URL,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/google_login/callback')
def callback():
    if not GOOGLE_CLIENT_ID:
        flash("Identifiants Google OAuth non configurés", "warning")
        return redirect(url_for('index'))
    
    try:
        # Récupération du code d'autorisation
        code = request.args.get("code")
        if not code:
            flash("Code d'autorisation manquant", "danger")
            return redirect(url_for('index'))
            
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Préparation de la requête d'échange de token
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=REDIRECT_URL,
            code=code,
        )
        
        # Échange du code contre un token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        if token_response.status_code != 200:
            flash("Erreur lors de l'échange du token", "danger")
            return redirect(url_for('index'))

        # Analyse de la réponse
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Récupération des informations utilisateur
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.status_code != 200:
            flash("Erreur lors de la récupération des informations utilisateur", "danger")
            return redirect(url_for('index'))
            
        userinfo = userinfo_response.json()

        # Vérification et traitement des informations utilisateur
        if userinfo.get("email_verified"):
            user_email = userinfo["email"]
            user_name = userinfo.get("given_name", user_email.split('@')[0])
        else:
            flash("L'adresse email n'est pas vérifiée par Google", "danger")
            return redirect(url_for('index'))

        # Recherche ou création de l'utilisateur
        user = User.query.filter_by(email=user_email).first()
        if not user:
            user = User(
                username=user_name,
                email=user_email,
                oauth_provider="google",
                oauth_id=userinfo.get("sub")
            )
            db.session.add(user)
            db.session.commit()
        
        # Mise à jour de la dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Connexion de l'utilisateur
        login_user(user)
        flash(f"Bienvenue, {user.username}!", "success")
        
        # Redirection vers la page demandée ou la page d'accueil
        next_page = session.get('next_url', url_for('index'))
        return redirect(next_page)
        
    except Exception as e:
        app.logger.error(f"Erreur OAuth Google: {e}")
        flash("Erreur de connexion. Veuillez réessayer.", "danger")
        return redirect(url_for('index'))

@auth_bp.route('/@auth_bp.route('/login')
def login():
    if not GOOGLE_CLIENT_ID:
        flash("Identifiants Google OAuth non configurés", "warning")
        return redirect(url_for('index'))
    
    # Authentification Google
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Préparation de la requête d'autorisation
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URL,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/google_login/callback')
def callback():
    if not GOOGLE_CLIENT_ID:
        flash("Identifiants Google OAuth non configurés", "warning")
        return redirect(url_for('index'))
    
    try:
        # Récupération du code d'autorisation
        code = request.args.get("code")
        if not code:
            flash("Code d'autorisation manquant", "danger")
            return redirect(url_for('index'))
            
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Préparation de la requête d'échange de token
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url.replace('http://', 'https://'),
            redirect_url=REDIRECT_URL,
            code=code,
        )
        
        # Échange du code contre un token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        if token_response.status_code != 200:
            flash("Erreur lors de l'échange du token", "danger")
            return redirect(url_for('index'))

        # Analyse de la réponse
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Récupération des informations utilisateur
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            users_name = userinfo_response.json()["given_name"]
            
            # Créer ou récupérer l'utilisateur
            from models import User, db
            user = User.query.filter_by(oauth_id=unique_id).first()
            if not user:
                user = User(
                    oauth_id=unique_id,
                    username=users_name,
                    email=users_email,
                    oauth_provider="google",
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash(f"Bienvenue, {users_name}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Email non vérifié par Google", "danger")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"Erreur d'authentification: {str(e)}", "danger")
        return redirect(url_for('index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté", "info")
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return redirect(url_for('dashboard', section='profile'))

# Enregistrer le blueprint
def init_auth():
    from flask_login import LoginManager
    from replit_auth import make_replit_blueprint
    
    # Initialiser le gestionnaire de connexion
    login_manager = LoginManager()
    login_manager.init_app(current_app)
    login_manager.login_view = 'replit_auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)
    
    # Enregistrer le blueprint d'authentification Google
    current_app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Ajouter l'authentification Replit
    replit_bp = make_replit_blueprint()
    if replit_bp:
        current_app.register_blueprint(replit_bp, url_prefix='/auth')
        current_app.logger.info("Authentification Replit configurée avec succès")
    else:
        current_app.logger.warning("L'authentification Replit n'a pas pu être configurée")
    
    return login_manager")
    
    return login_manager