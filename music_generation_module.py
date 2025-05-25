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
Module de Génération Musicale pour NeuronasX

Ce module implémente les fonctionnalités de génération musicale
en utilisant le système D²STIB et l'intégration Ollama/ACE-Step.
"""

import os
import sys
import logging
import time
import json
import tempfile
import uuid
from typing import Dict, List, Optional, Union, Tuple, Any
import numpy as np
import threading

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicGenerationModule:
    """
    Module de génération musicale pour NeuronasX,
    utilisant le système D²STIB et l'intégration ACE-Step.
    """
    
    def __init__(self):
        """Initialise le module de génération musicale"""
        self.temp_dir = os.path.join(os.getcwd(), 'static', 'temp_audio')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configuration D2 pour le contrôle neuromorphique
        self.d2_params = {
            "activation": 0.5,  # Niveau d'activation D2 (0.0-1.0)
            "creative_balance": 0.5,  # Équilibre créatif/analytique (0.0-1.0)
            "stim_level": 0.0,  # Niveau de stimulation (0.0-1.0)
            "entropy": 0.3  # Niveau d'entropie (0.0-1.0)
        }
        
        # Historique des générations
        self.generation_history = []
        self.max_history = 50
        
        # Configuration D²STIB
        self.d2stib_enabled = True
        self.token_bottleneck = 10  # bits/seconde
        
        # Modèle utilisé
        self.model_type = "Simulation (ACE-Step)"
        self.simulation_mode = True
        
        # Essayer d'initialiser Ollama
        self.ollama_integration = None
        try:
            from ollama_integration import OllamaIntegration
            self.ollama_integration = OllamaIntegration()
            
            # Vérifier si nous avons une connexion
            if self.ollama_integration.connected:
                self.simulation_mode = False
                self.model_type = "Ollama (ACE-Step)"
                logger.info("Intégration Ollama initialisée pour la génération musicale")
            else:
                logger.info("Mode simulation activé (Ollama non connecté)")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser l'intégration Ollama: {e}")
            logger.info("Mode simulation activé pour la génération musicale")
            
        # Initialiser la mémoire quantique pour les motifs musicaux
        self.quantum_memory = None
        try:
            from quantum_memory import PrimeFactorizedQuantumMemory
            
            # Dimensions adaptées pour les caractéristiques musicales
            self.quantum_memory = PrimeFactorizedQuantumMemory(
                capacity=200,
                collapse_threshold=20,
                similarity_threshold=0.8,
                input_dim=256,
                d2_integration=True
            )
            
            logger.info("Mémoire quantique initialisée pour la génération musicale")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser la mémoire quantique: {e}")
        
        logger.info("Module de génération musicale initialisé")
    
    def set_d2_parameters(self, activation: Optional[float] = None, 
                         creative_balance: Optional[float] = None, 
                         stim_level: Optional[float] = None, 
                         entropy: Optional[float] = None) -> None:
        """
        Définit les paramètres D2 pour la génération musicale
        
        Args:
            activation: Niveau d'activation D2 (0.0-1.0)
            creative_balance: Équilibre créatif/analytique (0.0-1.0)
            stim_level: Niveau de stimulation (0.0-1.0)
            entropy: Niveau d'entropie (0.0-1.0)
        """
        if activation is not None:
            self.d2_params["activation"] = max(0.0, min(1.0, activation))
        if creative_balance is not None:
            self.d2_params["creative_balance"] = max(0.0, min(1.0, creative_balance))
        if stim_level is not None:
            self.d2_params["stim_level"] = max(0.0, min(1.0, stim_level))
        if entropy is not None:
            self.d2_params["entropy"] = max(0.0, min(1.0, entropy))
            
        logger.info(f"Paramètres D2 mis à jour: {self.d2_params}")
        
        # Propager les paramètres à l'intégration Ollama
        if self.ollama_integration:
            self.ollama_integration.set_d2_parameters(
                activation=self.d2_params["activation"],
                creative_balance=self.d2_params["creative_balance"],
                stim_level=self.d2_params["stim_level"],
                entropy=self.d2_params["entropy"]
            )
            
        # Propager les paramètres à la mémoire quantique
        if self.quantum_memory:
            self.quantum_memory.set_d2_parameters(
                activation=self.d2_params["activation"],
                entropy=self.d2_params["entropy"],
                stim_level=self.d2_params["stim_level"]
            )
    
    def _apply_d2stib_optimization(self, prompt: str) -> str:
        """
        Applique l'optimisation D²STIB au prompt musical
        
        Args:
            prompt: Description textuelle originale
            
        Returns:
            str: Prompt optimisé
        """
        if not self.d2stib_enabled:
            return prompt
            
        # Identifier les mots-clés musicaux importants
        musical_keywords = [
            "tempo", "rythme", "mélodie", "harmonique", "accord", "timbre",
            "orchestration", "instrument", "dynamique", "texture", "motif",
            "contrepoint", "tonalité", "progression", "crescendo", "diminuendo",
            "staccato", "legato", "pizzicato", "vibrato", "groove", "ambiance"
        ]
        
        # Calculer le coefficient D2 basé sur l'activation
        d2_coef = 0.5 + (self.d2_params["activation"] * 0.5)  # 0.5-1.0
        
        # Optimisation: garder les termes musicaux importants et réduire le reste
        words = prompt.split()
        if len(words) <= 10:  # Courts prompts restent intacts
            return prompt
            
        # Identifier les mots importants
        word_importance = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Mots musicaux sont importants
            is_musical = any(keyword in word_lower for keyword in musical_keywords)
            
            # Début et fin du prompt sont importants
            position_importance = 1.0 if i < 5 or i >= len(words) - 5 else 0.5
            
            # Mots longs sont généralement plus importants
            length_importance = min(1.0, len(word) / 8)
            
            # Calculer l'importance totale
            importance = (
                (1.0 if is_musical else 0.3) * 
                position_importance * 
                length_importance
            )
            
            word_importance.append((i, importance))
        
        # Trier par importance
        word_importance.sort(key=lambda x: x[1], reverse=True)
        
        # Calculer combien de mots garder basé sur le coefficient D2
        # et le goulot d'information (10 bits/s ≈ 2-3 mots/s)
        target_length = int(max(10, min(len(words), len(words) * d2_coef)))
        
        # Sélectionner les indices des mots à garder
        keep_indices = sorted([idx for idx, _ in word_importance[:target_length]])
        
        # Reconstruire le prompt optimisé
        optimized_words = []
        for i in range(len(words)):
            if i in keep_indices:
                optimized_words.append(words[i])
        
        optimized_prompt = " ".join(optimized_words)
        
        # Ajouter une note sur l'optimisation D²STIB
        logger.info(f"Optimisation D²STIB: {len(words)} → {len(optimized_words)} mots")
        
        return optimized_prompt
    
    def generate_music_from_text(self, prompt: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Génère de la musique à partir d'une description textuelle
        
        Args:
            prompt: Description de la musique à générer
            output_path: Chemin pour sauvegarder la sortie (optionnel)
            
        Returns:
            Optional[str]: Chemin vers le fichier audio généré ou None en cas d'erreur
        """
        # Appliquer l'optimisation D²STIB au prompt
        optimized_prompt = self._apply_d2stib_optimization(prompt)
        
        # Créer un fichier temporaire si aucun chemin n'est spécifié
        if not output_path:
            timestamp = int(time.time())
            output_path = os.path.join(self.temp_dir, f"neuronas_music_{timestamp}.wav")
            
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Si l'intégration Ollama est disponible, l'utiliser
        if self.ollama_integration and not self.simulation_mode:
            try:
                result = self.ollama_integration.generate_music(optimized_prompt, output_path)
                if result and result.get("success"):
                    # Ajouter à l'historique
                    self._add_to_history({
                        "type": "text_to_music",
                        "prompt": prompt,
                        "optimized_prompt": optimized_prompt,
                        "output_path": output_path,
                        "d2_params": self.d2_params.copy(),
                        "timestamp": time.time(),
                        "model": self.model_type,
                        "success": True
                    })
                    return output_path
            except Exception as e:
                logger.error(f"Erreur lors de la génération via Ollama: {e}")
                logger.info("Retour au mode simulation")
                self.simulation_mode = True
        
        # Mode simulation
        try:
            # Créer un fichier simulé
            self._simulate_music_generation(prompt, optimized_prompt, output_path)
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "text_to_music",
                "prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "output_path": output_path,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": True,
                "simulation": True
            })
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la simulation de génération musicale: {e}")
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "text_to_music",
                "prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "output_path": None,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": False,
                "error": str(e)
            })
            
            return None
    
    def generate_music_from_audio(self, audio_path: str, prompt: str = "", 
                                output_path: Optional[str] = None) -> Optional[str]:
        """
        Génère de la musique en se basant sur un fichier audio existant
        
        Args:
            audio_path: Chemin vers le fichier audio source
            prompt: Instructions supplémentaires (optionnel)
            output_path: Chemin pour sauvegarder la sortie (optionnel)
            
        Returns:
            Optional[str]: Chemin vers le fichier audio généré ou None en cas d'erreur
        """
        # Vérifier que le fichier existe
        if not os.path.exists(audio_path):
            logger.error(f"Fichier audio non trouvé: {audio_path}")
            return None
            
        # Appliquer l'optimisation D²STIB au prompt
        optimized_prompt = self._apply_d2stib_optimization(prompt) if prompt else ""
        
        # Créer un fichier temporaire si aucun chemin n'est spécifié
        if not output_path:
            timestamp = int(time.time())
            output_path = os.path.join(self.temp_dir, f"neuronas_music_{timestamp}.wav")
            
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Pour l'instant, en mode simulation uniquement
        try:
            # Créer un fichier simulé
            self._simulate_music_generation(prompt, optimized_prompt, output_path, audio_path)
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "audio_to_music",
                "prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "input_audio": audio_path,
                "output_path": output_path,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": True,
                "simulation": True
            })
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la simulation de génération à partir d'audio: {e}")
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "audio_to_music",
                "prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "input_audio": audio_path,
                "output_path": None,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": False,
                "error": str(e)
            })
            
            return None
    
    def describe_music(self, audio_path: str) -> Optional[str]:
        """
        Analyse et décrit un fichier audio
        
        Args:
            audio_path: Chemin vers le fichier audio à analyser
            
        Returns:
            Optional[str]: Description textuelle du contenu audio
        """
        # Vérifier que le fichier existe
        if not os.path.exists(audio_path):
            logger.error(f"Fichier audio non trouvé: {audio_path}")
            return None
            
        # Pour l'instant, en mode simulation uniquement
        try:
            # Générer une description simulée
            description = self._simulate_music_description(audio_path)
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "music_description",
                "input_audio": audio_path,
                "description": description,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": True,
                "simulation": True
            })
            
            return description
            
        except Exception as e:
            logger.error(f"Erreur lors de la simulation de description musicale: {e}")
            
            # Ajouter à l'historique
            self._add_to_history({
                "type": "music_description",
                "input_audio": audio_path,
                "d2_params": self.d2_params.copy(),
                "timestamp": time.time(),
                "model": self.model_type,
                "success": False,
                "error": str(e)
            })
            
            return None
    
    def get_generation_status(self) -> Dict:
        """
        Récupère le statut actuel du générateur de musique
        
        Returns:
            Dict: Informations sur le statut
        """
        return {
            "d2_params": self.d2_params,
            "d2stib_enabled": self.d2stib_enabled,
            "token_bottleneck": self.token_bottleneck,
            "model_type": self.model_type,
            "simulation_mode": self.simulation_mode,
            "history_count": len(self.generation_history),
            "quantum_memory": bool(self.quantum_memory),
            "ollama_integration": bool(self.ollama_integration)
        }
    
    def get_generation_history(self, limit: int = 10) -> List[Dict]:
        """
        Récupère l'historique de génération
        
        Args:
            limit: Nombre maximum d'entrées à récupérer
            
        Returns:
            List[Dict]: Historique des générations
        """
        return self.generation_history[-limit:]
    
    def _add_to_history(self, entry: Dict) -> None:
        """
        Ajoute une entrée à l'historique de génération
        
        Args:
            entry: Informations sur la génération
        """
        # Ajouter l'ID unique
        entry["id"] = str(uuid.uuid4())
        
        # Ajouter au début de l'historique
        self.generation_history.append(entry)
        
        # Limiter la taille de l'historique
        if len(self.generation_history) > self.max_history:
            self.generation_history = self.generation_history[-self.max_history:]
    
    def _simulate_music_generation(self, prompt: str, optimized_prompt: str, 
                                 output_path: str, input_audio: Optional[str] = None) -> None:
        """
        Simule la génération de musique
        
        Args:
            prompt: Prompt original
            optimized_prompt: Prompt optimisé
            output_path: Chemin de sortie
            input_audio: Chemin vers l'audio d'entrée (optionnel)
        """
        # Créer un fichier texte de simulation au lieu d'un vrai audio
        with open(output_path, 'w') as f:
            f.write(f"# Fichier audio simulé (NeuronasX)\n")
            f.write(f"# Timestamp: {time.time()}\n")
            f.write(f"# Mode: {'audio_to_music' if input_audio else 'text_to_music'}\n")
            f.write(f"# Modèle: {self.model_type}\n\n")
            
            f.write(f"## Prompt Original\n{prompt}\n\n")
            f.write(f"## Prompt Optimisé (D²STIB)\n{optimized_prompt}\n\n")
            
            f.write(f"## Paramètres D2\n")
            for key, value in self.d2_params.items():
                f.write(f"# {key}: {value}\n")
                
            if input_audio:
                f.write(f"\n## Fichier Audio Source\n{input_audio}\n")
                
            f.write(f"\n## Simulation de Génération Musicale\n")
            f.write(f"# Cette simulation représente une séquence musicale qui aurait été\n")
            f.write(f"# générée par un modèle ACE-Step avec paramètres D2 spécifiés.\n")
            f.write(f"# En mode réel, un fichier audio WAV serait généré ici.\n")
            
        # Simuler un délai pour rendre la simulation plus réaliste
        time.sleep(1)
    
    def _simulate_music_description(self, audio_path: str) -> str:
        """
        Simule l'analyse et la description d'un fichier audio
        
        Args:
            audio_path: Chemin vers le fichier audio
            
        Returns:
            str: Description simulée
        """
        # Obtenir quelques informations sur le fichier
        file_size = os.path.getsize(audio_path)
        file_name = os.path.basename(audio_path)
        
        # Créer une description simulée
        tempo_options = ["lent", "modéré", "rapide", "variable"]
        tempo = tempo_options[file_size % len(tempo_options)]
        
        mood_options = ["mélancolique", "joyeux", "énergique", "contemplatif", "mystérieux"]
        mood = mood_options[(file_size // 1000) % len(mood_options)]
        
        instrument_options = [
            "piano", "guitare", "violon", "synthétiseur", "percussion", 
            "orchestre", "voix", "ensemble acoustique", "ensemble électronique"
        ]
        instruments = [
            instrument_options[(file_size // 100) % len(instrument_options)],
            instrument_options[(file_size // 10000) % len(instrument_options)]
        ]
        
        # Générer une description
        description = f"""
Le fichier audio {file_name} présente une composition musicale à tempo {tempo} 
avec une ambiance {mood}. Les instruments dominants semblent être {instruments[0]} 
et {instruments[1]}. La structure comprend une introduction progressive, 
suivie d'un développement thématique et d'une résolution harmonique.

Caractéristiques principales:
- Tempo: {tempo}
- Ambiance: {mood}
- Instrumentation: {instruments[0]}, {instruments[1]}
- Dynamique: modulation d'intensité avec nuances expressives
- Tonalité: {"majeure" if file_size % 2 == 0 else "mineure"} avec progressions harmoniques {"conventionnelles" if file_size % 3 == 0 else "innovantes"}

Cette composition pourrait correspondre à un genre musical de type 
{"classique contemporain" if file_size % 5 == 0 else "ambient expérimental" if file_size % 5 == 1 else "électronique minimaliste" if file_size % 5 == 2 else "jazz fusion" if file_size % 5 == 3 else "folk progressif"}.
"""
        
        # Simuler un délai pour rendre la simulation plus réaliste
        time.sleep(1)
        
        return description


# Test du module si exécuté directement
if __name__ == "__main__":
    # Créer une instance du module de génération musicale
    music_generator = MusicGenerationModule()
    
    # Tester la génération à partir de texte
    prompt = "Une mélodie de piano douce et contemplative, avec des cordes légères en arrière-plan, créant une atmosphère nostalgique comme un souvenir d'enfance"
    output_path = music_generator.generate_music_from_text(prompt)
    
    if output_path:
        print(f"Fichier généré: {output_path}")
        
        # Tester la description musicale
        description = music_generator.describe_music(output_path)
        print("\nDescription musicale:")
        print(description)
    else:
        print("Échec de la génération")