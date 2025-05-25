"""
Routes de génération musicale pour NeuronasX

Ce module fournit les routes pour l'API de génération musicale,
intégrant ACE-Step et le système D²STIB.
"""

import os
import logging
import json
import time
from flask import Blueprint, request, jsonify, render_template, current_app, send_file
from werkzeug.utils import secure_filename

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer le blueprint
music_bp = Blueprint('music', __name__, url_prefix='/api/music')

# Répertoire temporaire pour les fichiers audio
TEMP_AUDIO_DIR = os.path.join(os.getcwd(), 'static', 'temp_audio')
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

@music_bp.route('/generate', methods=['POST'])
def generate_music():
    """
    Génère de la musique à partir d'un texte ou d'un fichier audio
    
    Paramètres de requête (JSON ou form-data):
    - prompt: Description textuelle de la musique à générer
    - mode: 'text' (par défaut) ou 'audio'
    - d2_params: Paramètres D2 (optionnel, JSON)
    - audio_file: Fichier audio (uniquement pour le mode 'audio')
    
    Retourne:
    - JSON avec le chemin vers le fichier audio généré
    """
    try:
        # Vérifier si la requête est multipart (pour les fichiers)
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        
        # Extraire les paramètres selon le type de requête
        if is_multipart:
            prompt = request.form.get('prompt', '')
            mode = request.form.get('mode', 'text')
            d2_params_str = request.form.get('d2_params', '{}')
            
            try:
                d2_params = json.loads(d2_params_str)
            except json.JSONDecodeError:
                d2_params = {}
            
            audio_file = request.files.get('audio_file')
        else:
            data = request.json or {}
            prompt = data.get('prompt', '')
            mode = data.get('mode', 'text')
            d2_params = data.get('d2_params', {})
            audio_file = None
        
        # Vérifier les paramètres requis
        if not prompt and mode == 'text':
            return jsonify({
                'success': False,
                'error': 'Une description textuelle est requise pour le mode texte'
            }), 400
        
        if mode == 'audio' and (not is_multipart or not audio_file):
            return jsonify({
                'success': False,
                'error': 'Un fichier audio est requis pour le mode audio'
            }), 400
        
        # Initialiser le module de génération musicale si nécessaire
        if not hasattr(current_app, 'music_generator'):
            from music_generation_module import MusicGenerationModule
            current_app.music_generator = MusicGenerationModule()
        
        # Mettre à jour les paramètres D2 si fournis
        if d2_params:
            current_app.music_generator.set_d2_parameters(
                activation=d2_params.get('activation'),
                creative_balance=d2_params.get('creative_balance'),
                stim_level=d2_params.get('stim_level'),
                entropy=d2_params.get('entropy')
            )
        
        # Générer la musique selon le mode
        if mode == 'text':
            # Génération à partir du texte
            timestamp = int(time.time())
            output_path = os.path.join(TEMP_AUDIO_DIR, f'neuronas_music_{timestamp}.wav')
            
            result_path = current_app.music_generator.generate_music_from_text(
                prompt=prompt,
                output_path=output_path
            )
            
        else:
            # Génération à partir d'un fichier audio
            if audio_file:
                # Sauvegarder le fichier audio téléchargé
                audio_filename = secure_filename(audio_file.filename)
                timestamp = int(time.time())
                input_path = os.path.join(TEMP_AUDIO_DIR, f'input_{timestamp}_{audio_filename}')
                audio_file.save(input_path)
                
                # Définir le chemin de sortie
                output_path = os.path.join(TEMP_AUDIO_DIR, f'neuronas_music_{timestamp}.wav')
                
                # Générer à partir de l'audio
                result_path = current_app.music_generator.generate_music_from_audio(
                    audio_path=input_path,
                    prompt=prompt,
                    output_path=output_path
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'Fichier audio manquant'
                }), 400
        
        if not result_path:
            return jsonify({
                'success': False,
                'error': 'Échec de la génération de musique'
            }), 500
        
        # Créer l'URL relative pour le fichier audio
        relative_path = os.path.relpath(result_path, os.getcwd())
        web_path = '/' + relative_path.replace('\\', '/')
        
        # Récupérer le statut du générateur
        generator_status = current_app.music_generator.get_generation_status()
        
        return jsonify({
            'success': True,
            'audio_path': web_path,
            'prompt': prompt,
            'mode': mode,
            'd2_params': generator_status['d2_params'],
            'timestamp': time.time(),
            'model_type': generator_status['model_type'],
            'd2stib_enabled': generator_status['d2stib_enabled']
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de musique: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@music_bp.route('/status', methods=['GET'])
def get_status():
    """
    Récupère le statut du module de génération musicale
    
    Retourne:
    - JSON avec les informations de statut
    """
    try:
        # Initialiser le module si nécessaire
        if not hasattr(current_app, 'music_generator'):
            from music_generation_module import MusicGenerationModule
            current_app.music_generator = MusicGenerationModule()
        
        # Récupérer le statut
        status = current_app.music_generator.get_generation_status()
        
        # Vérifier si Ollama est disponible
        if not hasattr(current_app, 'ollama_integration'):
            try:
                from ollama_integration import OllamaIntegration
                current_app.ollama_integration = OllamaIntegration()
                ollama_status = current_app.ollama_integration.get_status()
            except Exception as e:
                logger.warning(f"Erreur lors de l'initialisation d'Ollama: {e}")
                ollama_status = {
                    "connected": False,
                    "error": str(e)
                }
        else:
            ollama_status = current_app.ollama_integration.get_status()
        
        return jsonify({
            'success': True,
            'generator_status': status,
            'ollama_status': ollama_status
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@music_bp.route('/describe', methods=['POST'])
def describe_audio():
    """
    Analyse et décrit un fichier audio
    
    Paramètres de requête (multipart/form-data):
    - audio_file: Fichier audio à analyser
    
    Retourne:
    - JSON avec la description de l'audio
    """
    try:
        # Vérifier si un fichier est fourni
        if 'audio_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier audio fourni'
            }), 400
            
        audio_file = request.files['audio_file']
        
        # Vérifier si le fichier est valide
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nom de fichier invalide'
            }), 400
            
        # Sauvegarder le fichier temporairement
        audio_filename = secure_filename(audio_file.filename)
        timestamp = int(time.time())
        audio_path = os.path.join(TEMP_AUDIO_DIR, f'analysis_{timestamp}_{audio_filename}')
        audio_file.save(audio_path)
        
        # Initialiser le module si nécessaire
        if not hasattr(current_app, 'music_generator'):
            from music_generation_module import MusicGenerationModule
            current_app.music_generator = MusicGenerationModule()
            
        # Analyser l'audio
        description = current_app.music_generator.describe_music(audio_path)
        
        return jsonify({
            'success': True,
            'description': description,
            'filename': audio_filename
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse audio: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@music_bp.route('/set_d2_params', methods=['POST'])
def set_d2_params():
    """
    Définit les paramètres D2 pour la génération musicale
    
    Paramètres de requête (JSON):
    - activation: Niveau d'activation D2 (0.0-1.0)
    - creative_balance: Équilibre créatif/analytique (0.0-1.0)
    - stim_level: Niveau de stimulation (0.0-1.0)
    - entropy: Niveau d'entropie (0.0-1.0)
    
    Retourne:
    - JSON avec les paramètres mis à jour
    """
    try:
        data = request.json or {}
        
        # Initialiser le module si nécessaire
        if not hasattr(current_app, 'music_generator'):
            from music_generation_module import MusicGenerationModule
            current_app.music_generator = MusicGenerationModule()
            
        # Mettre à jour les paramètres
        current_app.music_generator.set_d2_parameters(
            activation=data.get('activation'),
            creative_balance=data.get('creative_balance'),
            stim_level=data.get('stim_level'),
            entropy=data.get('entropy')
        )
        
        # Récupérer les paramètres mis à jour
        status = current_app.music_generator.get_generation_status()
        
        return jsonify({
            'success': True,
            'd2_params': status['d2_params']
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la définition des paramètres D2: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_music_routes(app):
    """
    Enregistre les routes de génération musicale dans l'application
    
    Args:
        app: Application Flask
    """
    # Enregistrer le blueprint
    app.register_blueprint(music_bp)
    
    # Ajouter la route pour l'interface de génération musicale
    @app.route('/music')
    def music_generation_view():
        """Interface de génération musicale"""
        return render_template('music_generation.html')
        
    return app