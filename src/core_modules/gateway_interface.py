"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

"""
Interface de passerelle pour le moteur cognitif Neuronas.
Gère la communication entre les composants du système.
"""
import logging
import json
from datetime import datetime
from flask import g
from core_modules.core_engine import CognitiveEngine, CoreStorageManager

logger = logging.getLogger(__name__)

class GatewayInterface:
    """
    Interface de passerelle pour le traitement des commandes et l'interaction avec le moteur cognitif.
    Sert de point d'entrée principal pour toutes les requêtes adressées au système Neuronas.
    """
    def __init__(self):
        """Initialise l'interface de passerelle"""
        logger.info("Interface de passerelle initialisée")
        self.cognitive_engine = CognitiveEngine()
        self.storage = CoreStorageManager()
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration du système depuis le fichier de configuration"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
                logger.info("Configuration chargée avec succès")
        except Exception as e:
            logger.warning(f"Erreur lors du chargement de la configuration: {e}")
            self.config = {
                "core": {
                    "activation_threshold": 0.5,
                    "entropy_baseline": 0.2,
                    "d2_baseline": 0.5
                }
            }
    
    def process_query(self, query, session_id=None):
        """
        Traite une requête utilisateur.
        
        Args:
            query (str): Requête utilisateur
            session_id (str): ID de session
            
        Returns:
            dict: Résultat du traitement
        """
        # Obtenir les paramètres utilisateur si disponibles
        user_settings = self._get_user_settings()
        if user_settings:
            self.cognitive_engine.set_user_settings(user_settings)
        
        # Traiter la requête
        result = self.cognitive_engine.process_query(query, session_id)
        
        # Stocker le résultat pour référence future
        if session_id:
            self.storage.store({
                'query': query,
                'response': result['response'],
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id
            })
        
        return result
    
    def _get_user_settings(self):
        """
        Récupère les paramètres de l'utilisateur actuel.
        
        Returns:
            dict: Paramètres utilisateur ou None
        """
        # Essayer d'obtenir l'utilisateur actuel depuis Flask
        if hasattr(g, 'user') and g.user:
            return {
                'd2_temperature': g.user.d2_temperature,
                'hemisphere_balance': g.user.hemisphere_balance,
                'creativity_weight': g.user.creativity_weight,
                'analytical_weight': g.user.analytical_weight
            }
        return None
    
    def run_command(self, command, data=""):
        """
        Exécute une commande spécifique dans le système Neuronas.
        
        Args:
            command (str): Commande à exécuter
            data (str): Données associées à la commande
            
        Returns:
            dict: Résultat de la commande
        """
        if command == "status":
            return {
                "status": "ok",
                "cognitive_engine": "active",
                "storage": "active",
                "mode": self.cognitive_engine.get_state()['mode']
            }
        elif command == "modulate":
            mode = data if data in ["stim", "pin", "balanced"] else "balanced"
            self.cognitive_engine.modulate(mode)
            return {
                "status": "ok",
                "mode": mode,
                "state": self.cognitive_engine.get_state()
            }
        elif command == "memory_stats":
            # Cette fonction serait implémentée pour récupérer les statistiques de mémoire
            return {
                "status": "ok",
                "stats": {
                    "L1": 42,  # Nombre d'entrées dans L1 (simulations)
                    "L2": 156,
                    "L3": 278
                }
            }
        else:
            logger.warning(f"Commande inconnue: {command}")
            return {
                "status": "error",
                "message": f"Commande inconnue: {command}"
            }