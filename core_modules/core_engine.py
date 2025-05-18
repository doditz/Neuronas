"""
Module principal du moteur cognitif Neuronas.
Implémente les fonctionnalités de base du système cognitif.
"""
import random
import logging
import json
import numpy as np
from datetime import datetime
from flask import g

logger = logging.getLogger(__name__)

class CognitiveEngine:
    """
    Moteur cognitif principal qui simule les fonctions du striatum, du cortex et de l'hippocampe.
    Implémente les capacités cognitives fondamentales du système Neuronas.
    """
    def __init__(self):
        self.state = {
            'mode': 'balanced',  # 'stim', 'pin', ou 'balanced'
            'focus': 0.5,        # Niveau de focus (0.0-1.0)
            'entropy': 0.2,      # Niveau d'entropie (0.0-1.0)
            'activation': {
                'left_hemisphere': 0.5,   # Activation hémisphère gauche
                'right_hemisphere': 0.5,  # Activation hémisphère droit
            }
        }
        self.user_settings = None
        logger.info("Moteur cognitif initialisé avec succès")
    
    def modulate(self, mode):
        """
        Module l'état cognitif en fonction du mode spécifié.
        
        Args:
            mode (str): Le mode de modulation ('stim', 'pin', ou 'balanced')
        """
        # Mettre à jour l'état cognitif
        self.state['mode'] = mode
        
        if mode == 'stim':
            # D2Stim - Dopaminergic Stimulation
            self.state['focus'] = 0.3
            self.state['entropy'] = 0.7
            self.state['activation']['left_hemisphere'] = 0.3
            self.state['activation']['right_hemisphere'] = 0.8
            logger.info("D2Stim activé - Traitement créatif priorisé")
        elif mode == 'pin':
            # D2Pin - Dopaminergic Inhibition
            self.state['focus'] = 0.8
            self.state['entropy'] = 0.2
            self.state['activation']['left_hemisphere'] = 0.8
            self.state['activation']['right_hemisphere'] = 0.3
            logger.info("D2Pin activé - Traitement analytique priorisé")
        else:
            # Balanced - Équilibre
            self.state['focus'] = 0.5
            self.state['entropy'] = 0.4
            self.state['activation']['left_hemisphere'] = 0.5
            self.state['activation']['right_hemisphere'] = 0.5
            logger.info("Mode équilibré activé")
        
        return self.state
    
    def analyze(self, text):
        """
        Analyse le texte d'entrée et retourne des métriques cognitives.
        
        Args:
            text (str): Texte à analyser
        
        Returns:
            dict: Résultats d'analyse incluant score et mode de modulation
        """
        # Analyse simplifiée du texte
        words = text.lower().split()
        
        # Mots-clés analytiques et créatifs
        analytical_keywords = ['analyser', 'calculer', 'evaluer', 'logique', 'raisonner', 
                               'analyze', 'calculate', 'evaluate', 'facts', 'logic', 'reason']
        creative_keywords = ['creer', 'imaginer', 'innover', 'inspirer', 'rever', 
                            'create', 'imagine', 'innovate', 'inspire', 'dream']
        
        # Calculer les scores
        analytical_score = sum(1 for word in words if any(keyword in word for keyword in analytical_keywords))
        creative_score = sum(1 for word in words if any(keyword in word for keyword in creative_keywords))
        
        # Normaliser les scores
        total_score = max(1, analytical_score + creative_score)
        normalized_analytical = analytical_score / total_score
        normalized_creative = creative_score / total_score
        
        # Déterminer le type de requête
        if normalized_analytical > normalized_creative:
            query_type = 'analytical'
            hemisphere = 'L'
        elif normalized_creative > normalized_analytical:
            query_type = 'creative'
            hemisphere = 'R'
        else:
            query_type = 'balanced'
            hemisphere = 'C'
        
        # Appliquer les préférences utilisateur si disponibles
        if self.user_settings:
            # Ajuster les scores en fonction des préférences
            analytical_factor = self.user_settings.get('analytical_weight', 0.5)
            creative_factor = self.user_settings.get('creativity_weight', 0.5)
            
            normalized_analytical = normalized_analytical * analytical_factor
            normalized_creative = normalized_creative * creative_factor
            
            # Recalculer le type de requête
            if normalized_analytical > normalized_creative:
                query_type = 'analytical'
                hemisphere = 'L'
            elif normalized_creative > normalized_analytical:
                query_type = 'creative'
                hemisphere = 'R'
        
        # Préparer le résultat
        d2_activation = self.state['focus']
        
        result = {
            'query_type': query_type,
            'hemisphere_used': hemisphere,
            'd2_activation': d2_activation,
            'scores': {
                'analytical': normalized_analytical,
                'creative': normalized_creative
            }
        }
        
        return result
    
    def process_query(self, query, session_id=None):
        """
        Traite une requête cognitive et génère une réponse.
        
        Args:
            query (str): La requête à traiter
            session_id (str): ID de session optionnel
            
        Returns:
            dict: Réponse et métadonnées associées
        """
        # Vérifier les commandes spéciales
        if query.lower().startswith('modulate '):
            mode = query.lower().split(' ')[1]
            if mode in ['stim', 'pin', 'balanced']:
                self.modulate(mode)
                return {
                    'response': f"Mode cognitif modulé à {mode}",
                    'query_type': 'system',
                    'hemisphere_used': 'C',
                    'processing_time': 0.1,
                    'd2_activation': self.state['focus'],
                    'focus': self.state['focus'],
                    'entropy': self.state['entropy']
                }
        
        # Analyser la requête
        analysis = self.analyze(query)
        
        # Déterminer le traitement en fonction de l'analyse
        if analysis['hemisphere_used'] == 'L':
            # Traitement analytique (hémisphère gauche)
            response = self._process_analytical(query)
        elif analysis['hemisphere_used'] == 'R':
            # Traitement créatif (hémisphère droit)
            response = self._process_creative(query)
        else:
            # Traitement équilibré
            response = self._process_balanced(query)
        
        # Simuler le temps de traitement
        processing_time = random.uniform(0.1, 2.0)
        
        return {
            'response': response,
            'query_type': analysis['query_type'],
            'hemisphere_used': analysis['hemisphere_used'],
            'processing_time': processing_time,
            'd2_activation': analysis['d2_activation']
        }
    
    def _process_analytical(self, query):
        """Traitement analytique pour l'hémisphère gauche"""
        # Simulation d'une réponse analytique
        responses = [
            f"Après analyse méthodique, je peux indiquer que {query} implique plusieurs facteurs clés à considérer. Premièrement, l'approche structurée suggère une organisation hiérarchique des concepts. Deuxièmement, les données empiriques confirment une corrélation significative entre les variables principales.",
            f"En examinant {query} de manière analytique, je note trois dimensions fondamentales: la structure logique sous-jacente, la cohérence des termes employés, et les implications déductives qui en découlent. Cette catégorisation permet une compréhension systématique du sujet.",
            f"L'analyse factuelle de {query} révèle un cadre conceptuel spécifique. Les principes fondamentaux peuvent être décomposés en composantes discrètes, chacune caractérisée par des attributs mesurables et vérifiables par observation empirique.",
            f"En considérant {query} selon une perspective analytique, je formule l'hypothèse suivante: les éléments constitutifs forment un système cohérent dont les propriétés émergentes peuvent être modélisées mathématiquement avec un degré raisonnable de précision."
        ]
        return random.choice(responses)
    
    def _process_creative(self, query):
        """Traitement créatif pour l'hémisphère droit"""
        # Simulation d'une réponse créative
        responses = [
            f"En explorant {query} de façon imaginative, je vois un horizon de possibilités non conventionnelles. Les connections inattendues entre concepts dissemblables révèlent des motifs inspirants qui dépassent les cadres traditionnels de pensée.",
            f"Ce que suggère {query} m'évoque une constellation d'idées interconnectées, chacune vibrant avec un potentiel transformateur. Les frontières conceptuelles s'estompent pour laisser place à une vision holistique où l'intuition guide la découverte.",
            f"{query} peut être réimaginé comme une danse d'éléments en constante évolution. Si nous abandonnons momentanément nos présupposés, des perspectives révolutionnaires émergent, illuminant des chemins inexplorés vers l'innovation.",
            f"En embrassant pleinement la nature métaphorique de {query}, nous découvrons des résonances subtiles avec des phénomènes apparemment sans relation. Cette vision kaléidoscopique enrichit notre compréhension et catalyse l'émergence d'idées novatrices."
        ]
        return random.choice(responses)
    
    def _process_balanced(self, query):
        """Traitement équilibré utilisant les deux hémisphères"""
        # Simulation d'une réponse équilibrée
        responses = [
            f"En considérant {query}, je propose une analyse équilibrée qui intègre à la fois rigueur analytique et perspectives créatives. Les données suggèrent certaines tendances quantifiables, tandis que l'approche intuitive révèle des modèles émergents qui méritent exploration.",
            f"{query} présente des aspects logiquement structurés qui bénéficient d'une analyse systématique, ainsi que des dimensions plus abstraites qui s'illuminent à travers une approche intuitive. Cette dualité offre une compréhension plus riche et nuancée.",
            f"En examinant {query} avec une perspective intégrée, je distingue une architecture conceptuelle où la précision analytique et l'exploration créative se complètent harmonieusement, produisant une compréhension qui transcende les limites d'une approche unique.",
            f"L'analyse de {query} révèle un équilibre fascinant entre éléments quantifiables et intuitions qualitatives. Cette symbiose cognitive permet d'appréhender le sujet dans sa complexité multidimensionnelle, honorant à la fois sa structure logique et sa richesse conceptuelle."
        ]
        return random.choice(responses)
    
    def reflect(self, data):
        """
        Effectue un traitement cognitif réflexif sur les données d'entrée.
        
        Args:
            data (str): Données d'entrée pour réflexion
        
        Returns:
            str: Sortie de réflexion
        """
        # Implémenter plus tard une vraie réflexion
        return f"Réflexion sur: {data}"
    
    def get_state(self):
        """Retourne l'état cognitif actuel"""
        return self.state
    
    def process_feedback(self, hypothesis, feedback_value):
        """
        Traite les feedbacks pour l'apprentissage par renforcement via BRONAS.
        
        Args:
            hypothesis (str): L'hypothèse évaluée
            feedback_value (float): Score de feedback entre -1.0 et 1.0
        """
        # Implémentation simplifiée pour le moment
        logger.info(f"Feedback reçu pour l'hypothèse: {hypothesis}, valeur: {feedback_value}")
        return True
    
    def set_user_settings(self, settings):
        """
        Définit les paramètres utilisateur pour personnaliser le traitement cognitif.
        
        Args:
            settings (dict): Paramètres utilisateur
        """
        self.user_settings = settings
        return True

class StorageManager:
    """
    Gestionnaire pour le stockage multi-tier et les opérations de mémoire.
    """
    def __init__(self):
        """Initialise le gestionnaire de stockage"""
        logger.info("Gestionnaire de stockage initialisé")
    
    def store(self, data, tier=1, hemisphere='C'):
        """
        Stocke des données dans le tier et l'hémisphère spécifiés.
        
        Args:
            data (dict): Données à stocker
            tier (int): Niveau de stockage (1-3)
            hemisphere (str): Hémisphère ('L', 'R', ou 'C' pour central)
            
        Returns:
            bool: Succès du stockage
        """
        logger.info(f"Données stockées dans tier {tier}, hémisphère {hemisphere}")
        return True
    
    def retrieve(self, key, tier=1, hemisphere='C'):
        """
        Récupère des données du stockage.
        
        Args:
            key (str): Clé de recherche
            tier (int): Niveau de stockage (1-3)
            hemisphere (str): Hémisphère ('L', 'R', ou 'C' pour central)
            
        Returns:
            dict: Données récupérées ou None
        """
        # Implémentation factice pour le moment
        return {'key': key, 'value': f"Donnée associée à {key}"}

class GatewayInterface:
    """
    Interface de passerelle pour le traitement des commandes et l'interaction avec le moteur cognitif.
    """
    def __init__(self):
        """Initialise l'interface de passerelle"""
        logger.info("Interface de passerelle initialisée")
        self.cognitive_engine = CognitiveEngine()
        self.storage = StorageManager()
    
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