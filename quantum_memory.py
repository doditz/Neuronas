"""
Système de Mémoire Quantique pour NeuronasX

Ce module implémente un système de mémoire inspiré des principes quantiques,
utilisant la factorisation en nombres premiers pour une représentation efficace 
des chemins neuronaux et la détection de dérive conceptuelle.
"""

import torch
import numpy as np
from collections import OrderedDict
import time
import hashlib
from typing import Dict, List, Tuple, Union, Optional, Any
import threading
import logging
from sympy import primefactors, primerange
import json
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NeuronasX.QuantumMemory")

# Vérifier si FAISS est disponible, sinon utiliser une alternative
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS non disponible, utilisation d'alternatives pour la recherche de similarité")

# Vérifier si scipy est disponible
try:
    from scipy.sparse import csr_matrix
    from scipy.spatial.distance import cosine
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("SciPy non disponible, fonctionnalités limitées")

class PrimeFactorizedQuantumMemory:
    """
    Système de Mémoire à Effondrement Quantique utilisant la factorisation en nombres premiers
    pour une représentation efficace des chemins neuronaux et la gestion de mémoire.
    
    Intègre avec le système D²STIB de NeuronasX pour optimiser les goulots d'information.
    """
    
    def __init__(self, 
                 capacity: int = 1000, 
                 collapse_threshold: int = 30, 
                 similarity_threshold: float = 0.82,
                 input_dim: int = 768, 
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
                 use_sparse: bool = True,
                 collapse_refresh_rate: int = 500,
                 adaptive_threshold: bool = True,
                 max_collapsed_pathways: int = 200,
                 d2_integration: bool = True):
        """
        Initialiser le système de mémoire inspiré des principes quantiques.
        
        Args:
            capacity: Capacité maximale du cache
            collapse_threshold: Nombre minimum d'éléments avant d'envisager l'effondrement
            similarity_threshold: Seuil pour considérer des éléments similaires
            input_dim: Dimension des vecteurs d'entrée
            device: Périphérique à utiliser pour les opérations tensorielles
            use_sparse: Utiliser des représentations tensorielles creuses
            collapse_refresh_rate: Fréquence de rafraîchissement des chemins effondrés
            adaptive_threshold: Ajuster dynamiquement le seuil de similarité
            max_collapsed_pathways: Nombre maximum de chemins effondrés à maintenir
            d2_integration: Activer l'intégration avec le système D²STIB
        """
        self.capacity = capacity
        self.collapse_threshold = collapse_threshold
        self.similarity_threshold = similarity_threshold
        self.base_similarity_threshold = similarity_threshold
        self.device = device
        self.input_dim = input_dim
        self.use_sparse = use_sparse and SCIPY_AVAILABLE
        self.collapse_refresh_rate = collapse_refresh_rate
        self.adaptive_threshold = adaptive_threshold
        self.max_collapsed_pathways = max_collapsed_pathways
        self.d2_integration = d2_integration
        
        # Initialiser la recherche de nombres premiers pour la factorisation
        self.primes = list(primerange(2, 1000))
        
        # Initialiser l'index FAISS pour une recherche rapide de similarité
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(input_dim)
            self.collapsed_pathways_data = np.zeros((0, input_dim), dtype=np.float32)
        else:
            self.index = None
            self.collapsed_pathways_data = []
        
        # Stockage des chemins
        self.pathway_cache = OrderedDict()
        self.collapsed_ids = []
        self.collapsed_weights = []
        self.collapse_counts = []
        self.pathway_factors = {}
        self.pathway_entropy = {}
        self.pathway_vectors = {}
        self.temporal_versions = {}
        
        # Statistiques
        self.query_times = []
        self.cache_hits = 0
        self.collapse_hits = 0
        self.total_queries = 0
        self.computation_time_saved = 0
        self.query_history = []
        self.collapse_history = []
        
        # Verrou pour la sécurité des threads
        self.lock = threading.RLock()
        
        # Paramètres adaptatifs
        self.last_collapse_time = 0
        self.concept_drift_detected = False
        self.drift_detection_window = 1000
        self.drift_threshold = 0.15
        
        # Paramètres D²STIB
        self.d2_params = {
            "activation": 0.5,
            "entropy": 0.3,
            "stim_level": 0.0,
            "bottleneck_limit": 10.0  # bits/seconde
        }
        
        logger.info(f"Système de mémoire quantique initialisé avec {capacity} capacité, {collapse_threshold} seuil d'effondrement")
        
        # Créer le répertoire de sauvegarde si nécessaire
        self.save_dir = os.path.join(os.getcwd(), 'quantum_memory_cache')
        os.makedirs(self.save_dir, exist_ok=True)
    
    def set_d2_parameters(self, activation: float = None, entropy: float = None, 
                         stim_level: float = None, bottleneck_limit: float = None):
        """
        Définir les paramètres D2 pour la mémoire quantique
        
        Args:
            activation: Niveau d'activation D2 (0.0-1.0)
            entropy: Niveau d'entropie (0.0-1.0)
            stim_level: Niveau de stimulation (0.0-1.0)
            bottleneck_limit: Limite du goulot d'information en bits/seconde
        """
        if not self.d2_integration:
            return
            
        if activation is not None:
            self.d2_params["activation"] = max(0.0, min(1.0, activation))
            
            # D2 influence la sélection des chemins quantiques
            self.similarity_threshold = self.base_similarity_threshold * (1 - 0.2 * activation)
            
        if entropy is not None:
            self.d2_params["entropy"] = max(0.0, min(1.0, entropy))
            
            # Entropie influence la conservation des versions temporelles
            max_versions = 3 + int(entropy * 7)  # 3 à 10 versions selon l'entropie
            for hash_id in self.temporal_versions:
                if len(self.temporal_versions[hash_id]) > max_versions:
                    # Garder les versions les plus récentes
                    self.temporal_versions[hash_id] = self.temporal_versions[hash_id][-max_versions:]
                    
        if stim_level is not None:
            self.d2_params["stim_level"] = max(0.0, min(1.0, stim_level))
            
            # Niveau de stimulation influence le seuil d'effondrement
            self.collapse_threshold = int(self.collapse_threshold * (1 + stim_level * 0.5))
            
        if bottleneck_limit is not None:
            self.d2_params["bottleneck_limit"] = max(1.0, bottleneck_limit)
            
        logger.info(f"Paramètres D2 mis à jour: {self.d2_params}")
    
    def _factorize_pathway(self, weights: Union[torch.Tensor, List[torch.Tensor]]) -> int:
        """
        Créer une représentation unique par factorisation en nombres premiers des poids du chemin.
        
        Args:
            weights: Tenseur ou liste de tenseurs représentant les poids
            
        Returns:
            Entier représentant la signature factorisée
        """
        # Extraire les valeurs clés des poids (en utilisant les k valeurs absolues maximales)
        if isinstance(weights, list):
            flat_weights = torch.cat([w.flatten() for w in weights])
        else:
            flat_weights = weights.flatten()
            
        # Obtenir les k valeurs absolues maximales
        k = min(20, len(flat_weights))
        top_values, indices = torch.topk(torch.abs(flat_weights), k)
        
        # Créer une empreinte unique en utilisant la factorisation en nombres premiers
        signature = 1
        for i, idx in enumerate(indices):
            value = flat_weights[idx].item()
            # Convertir en entier et utiliser comme exposant pour le i-ème nombre premier
            exponent = int(np.abs(value) * 100) % 20
            signature *= self.primes[i] ** exponent
            
        return signature
    
    def _hash_input(self, x: torch.Tensor) -> str:
        """
        Créer un hachage efficace pour le tenseur d'entrée.
        
        Args:
            x: Tenseur d'entrée
            
        Returns:
            Représentation en chaîne du hachage
        """
        # Utiliser les k valeurs maximales pour un hachage plus rapide
        k = min(20, x.numel())
        if k == x.numel():
            x_flat = x.flatten()
        else:
            x_flat = torch.topk(torch.abs(x.flatten()), k)[1]
            
        # Convertir en numpy et hacher
        x_np = x_flat.detach().cpu().numpy().astype(np.float32)
        return hashlib.md5(x_np.tobytes()).hexdigest()
    
    def _vector_from_input(self, x: torch.Tensor) -> np.ndarray:
        """
        Extraire le vecteur de caractéristiques de l'entrée pour la comparaison de similarité.
        
        Args:
            x: Tenseur d'entrée
            
        Returns:
            Représentation NumPy du vecteur de caractéristiques
        """
        return x.detach().cpu().numpy().reshape(1, -1).astype(np.float32)
    
    def _compress_weights(self, weights: Union[torch.Tensor, List[torch.Tensor]]) -> Union[Any, np.ndarray, List[Union[Any, np.ndarray]]]:
        """
        Compresser les poids pour un stockage efficace.
        
        Args:
            weights: Tenseur ou liste de tenseurs à compresser
            
        Returns:
            Représentation compressée des poids
        """
        if not isinstance(weights, list):
            # Convertir en représentation creuse
            w_np = weights.detach().cpu().numpy()
            if self.use_sparse:
                return csr_matrix(w_np)
            else:
                return w_np
        else:
            # Gérer une liste de poids
            if self.use_sparse:
                return [csr_matrix(w.detach().cpu().numpy()) for w in weights]
            else:
                return [w.detach().cpu().numpy() for w in weights]
    
    def _decompress_weights(self, compressed_weights: Union[Any, np.ndarray, List[Union[Any, np.ndarray]]]) -> Union[torch.Tensor, List[torch.Tensor]]:
        """
        Décompresser les poids au format tenseur.
        
        Args:
            compressed_weights: Poids compressés à décompresser
            
        Returns:
            Tenseur ou liste de tenseurs
        """
        if not isinstance(compressed_weights, list):
            if self.use_sparse:
                w_np = compressed_weights.toarray()
            else:
                w_np = compressed_weights
            return torch.tensor(w_np).to(self.device)
        else:
            if self.use_sparse:
                return [torch.tensor(w.toarray()).to(self.device) for w in compressed_weights]
            else:
                return [torch.tensor(w).to(self.device) for w in compressed_weights]
    
    def _update_similarity_threshold(self):
        """Ajuster dynamiquement le seuil de similarité en fonction des performances du système"""
        if not self.adaptive_threshold or self.total_queries < 100:
            return
            
        # Calculer le taux de succès
        hit_rate = (self.cache_hits + self.collapse_hits) / max(1, self.total_queries)
        
        # Ajuster le seuil en fonction du taux de succès
        if hit_rate < 0.2:
            # Trop peu de succès, abaisser le seuil pour être plus indulgent
            self.similarity_threshold = max(0.65, self.similarity_threshold - 0.02)
        elif hit_rate > 0.8:
            # Trop de succès, augmenter le seuil pour être plus sélectif
            self.similarity_threshold = min(0.95, self.similarity_threshold + 0.01)
        
        # Vérifier si nous approchons des limites de mémoire
        if FAISS_AVAILABLE:
            memory_pressure = len(self.collapsed_pathways_data) / self.max_collapsed_pathways
        else:
            memory_pressure = len(self.collapsed_ids) / self.max_collapsed_pathways
            
        if memory_pressure > 0.9:
            # Sous haute pression mémoire, augmenter le seuil pour réduire les nouveaux chemins
            self.similarity_threshold = min(0.95, self.similarity_threshold + 0.03)
        
        logger.debug(f"Seuil de similarité ajusté à {self.similarity_threshold:.2f} (taux de succès: {hit_rate:.2f})")
    
    def _detect_concept_drift(self, x: torch.Tensor, input_hash: str) -> bool:
        """
        Détecter si le sens du concept dérive au fil du temps.
        
        Args:
            x: Tenseur d'entrée
            input_hash: Hachage de l'entrée
            
        Returns:
            Booléen indiquant si une dérive a été détectée
        """
        # Vérifier seulement périodiquement
        if self.total_queries % self.drift_detection_window != 0:
            return False
            
        # Besoin d'un historique suffisant
        if len(self.query_history) < self.drift_detection_window:
            return False
            
        # Vérifier si des requêtes similaires ont des représentations divergentes
        x_vec = self._vector_from_input(x)
        
        for old_hash, old_vec in self.pathway_vectors.items():
            if old_hash == input_hash:
                continue
                
            # Calculer la similarité
            if SCIPY_AVAILABLE:
                # Utiliser la distance cosinus de scipy
                sim = 1 - cosine(x_vec.flatten(), old_vec.flatten())
            else:
                # Calcul alternatif de similarité
                x_norm = np.linalg.norm(x_vec)
                old_norm = np.linalg.norm(old_vec)
                sim = np.dot(x_vec.flatten(), old_vec.flatten()) / (x_norm * old_norm)
            
            # Vérifier si nous avons un enregistrement de version temporelle
            if old_hash in self.temporal_versions and len(self.temporal_versions[old_hash]) > 1:
                oldest_vec = self.temporal_versions[old_hash][0]
                newest_vec = self.temporal_versions[old_hash][-1]
                
                # Calculer la dérive entre la version la plus ancienne et la plus récente
                if SCIPY_AVAILABLE:
                    version_sim = 1 - cosine(oldest_vec.flatten(), newest_vec.flatten())
                else:
                    oldest_norm = np.linalg.norm(oldest_vec)
                    newest_norm = np.linalg.norm(newest_vec)
                    version_sim = np.dot(oldest_vec.flatten(), newest_vec.flatten()) / (oldest_norm * newest_norm)
                
                if version_sim < (1 - self.drift_threshold):
                    logger.info(f"Dérive conceptuelle détectée pour {old_hash[:8]}, similarité: {version_sim:.2f}")
                    self.concept_drift_detected = True
                    return True
        
        return False
    
    def _manage_temporal_versioning(self, input_hash: str, x_vec: np.ndarray):
        """
        Maintenir des versions temporelles des concepts pour suivre la dérive.
        
        Args:
            input_hash: Hachage de l'entrée
            x_vec: Représentation vectorielle
        """
        if input_hash not in self.temporal_versions:
            self.temporal_versions[input_hash] = [x_vec]
        else:
            # Garder au maximum 5 versions pour suivre l'évolution (ou plus si entropie élevée)
            max_versions = 5
            if self.d2_integration:
                max_versions = 3 + int(self.d2_params["entropy"] * 7)  # 3 à 10 selon l'entropie
                
            if len(self.temporal_versions[input_hash]) >= max_versions:
                self.temporal_versions[input_hash].pop(0)
            self.temporal_versions[input_hash].append(x_vec)
    
    def query(self, x: torch.Tensor, expert_weights: Union[torch.Tensor, List[torch.Tensor]], 
             forward_func: callable) -> Tuple[torch.Tensor, Union[torch.Tensor, List[torch.Tensor]]]:
        """
        Interroger le système de mémoire avec l'entrée x et les poids experts actuels.
        
        Args:
            x: Tenseur d'entrée
            expert_weights: Poids pour le traitement
            forward_func: Fonction à appeler pour le traitement
            
        Returns:
            Tuple de (tenseur résultat, poids utilisés)
        """
        with self.lock:
            start_time = time.time()
            self.total_queries += 1
            result = None
            input_hash = self._hash_input(x)
            
            # Stocker la représentation vectorielle pour la similarité et la détection de dérive
            x_vec = self._vector_from_input(x)
            self.pathway_vectors[input_hash] = x_vec
            self._manage_temporal_versioning(input_hash, x_vec)
            
            # D²STIB: Ajuster les seuils de similarité basés sur l'activation D2
            if self.d2_integration and self.adaptive_threshold:
                # Plus d'activation = plus de créativité = seuil plus bas (plus de possibilités)
                d2_adjusted_threshold = self.similarity_threshold * (1 - 0.2 * self.d2_params["activation"])
            else:
                d2_adjusted_threshold = self.similarity_threshold
            
            # Vérifier le cache exact
            if input_hash in self.pathway_cache:
                # Cache hit
                result, compressed_weights = self.pathway_cache[input_hash]
                weights = self._decompress_weights(compressed_weights)
                
                # Déplacer à la fin (utilisé le plus récemment)
                self.pathway_cache.move_to_end(input_hash)
                self.cache_hits += 1
                
                # Mettre à jour l'entropie (plus certain)
                if input_hash in self.pathway_entropy:
                    self.pathway_entropy[input_hash] *= 0.9
            else:
                # Chercher dans les chemins effondrés
                similar_collapsed = False
                
                if len(self.collapsed_ids) > 0:
                    # Recherche dans les chemins effondrés
                    if FAISS_AVAILABLE and len(self.collapsed_pathways_data) > 0:
                        # Utiliser FAISS pour une recherche rapide
                        D, I = self.index.search(x_vec, min(5, len(self.collapsed_pathways_data)))
                        closest_idx = I[0][0]
                        distance = D[0][0]
                        similarity = 1.0 / (1.0 + distance)  # Convertir la distance en similarité
                        
                        if similarity > d2_adjusted_threshold:
                            similar_collapsed = True
                            collapsed_id = self.collapsed_ids[closest_idx]
                            weights = self._decompress_weights(self.collapsed_weights[closest_idx])
                            
                            # Exécuter avec les poids effondrés
                            result = forward_func(x, weights)
                            
                            # Incrémenter le compteur d'effondrement
                            self.collapse_counts[closest_idx] += 1
                            self.collapse_hits += 1
                    else:
                        # Recherche manuelle des chemins similaires
                        for i, collapsed_vec in enumerate(self.pathway_vectors.values()):
                            if i >= len(self.collapsed_ids):
                                break
                                
                            if SCIPY_AVAILABLE:
                                similarity = 1 - cosine(x_vec.flatten(), collapsed_vec.flatten())
                            else:
                                x_norm = np.linalg.norm(x_vec)
                                collapsed_norm = np.linalg.norm(collapsed_vec)
                                similarity = np.dot(x_vec.flatten(), collapsed_vec.flatten()) / (x_norm * collapsed_norm)
                            
                            if similarity > d2_adjusted_threshold:
                                similar_collapsed = True
                                weights = self._decompress_weights(self.collapsed_weights[i])
                                
                                # Exécuter avec les poids effondrés
                                result = forward_func(x, weights)
                                
                                # Incrémenter le compteur d'effondrement
                                self.collapse_counts[i] += 1
                                self.collapse_hits += 1
                                break
                
                # Si aucun chemin effondré n'est similaire, exécuter avec les poids d'expert
                if not similar_collapsed:
                    # Exécuter avec les poids d'expert
                    result = forward_func(x, expert_weights)
                    weights = expert_weights
                    
                    # Factoriser et stocker le chemin
                    pathway_factor = self._factorize_pathway(weights)
                    self.pathway_factors[input_hash] = pathway_factor
                    self.pathway_entropy[input_hash] = 1.0
                    
                    # Stocker dans le cache
                    compressed_weights = self._compress_weights(weights)
                    self.pathway_cache[input_hash] = (result, compressed_weights)
                    
                    # Vérifier si nous avons atteint la capacité
                    if len(self.pathway_cache) > self.capacity:
                        # Supprimer l'élément le moins récemment utilisé
                        oldest = next(iter(self.pathway_cache))
                        self.pathway_cache.pop(oldest)
                    
                    # Vérifier si nous devons effectuer un effondrement
                    current_time = time.time()
                    if (len(self.pathway_cache) > self.collapse_threshold and 
                            (current_time - self.last_collapse_time > self.collapse_refresh_rate)):
                        self._collapse_pathways()
                        self.last_collapse_time = current_time
            
            # Mettre à jour les statistiques
            query_time = time.time() - start_time
            self.query_times.append(query_time)
            
            # Stocker l'historique des requêtes
            self.query_history.append((input_hash, query_time))
            if len(self.query_history) > self.drift_detection_window:
                self.query_history.pop(0)
            
            # Mettre à jour les seuils adaptatifs
            if self.adaptive_threshold:
                self._update_similarity_threshold()
            
            # Vérifier la dérive conceptuelle
            self._detect_concept_drift(x, input_hash)
            
            return result, weights
    
    def _collapse_pathways(self):
        """Effondrer les chemins similaires pour optimiser la mémoire"""
        if len(self.pathway_cache) <= 1:
            return
            
        logger.info(f"Effondrement des chemins, taille du cache: {len(self.pathway_cache)}")
        
        # Récupérer les clés et les facteurs
        keys = list(self.pathway_cache.keys())
        factors = [self.pathway_factors.get(k, 0) for k in keys]
        
        # Regrouper par facteurs similaires
        factor_groups = {}
        for i, factor in enumerate(factors):
            # Ignorer les facteurs nuls
            if factor == 0:
                continue
                
            # Trouver un groupe pour ce facteur
            assigned = False
            for group_factor, group_indices in factor_groups.items():
                # Comparer les facteurs premiers communs
                common_primes = set(primefactors(factor)) & set(primefactors(group_factor))
                if len(common_primes) >= 3:  # Considérer similaire si au moins 3 facteurs premiers communs
                    group_indices.append(i)
                    assigned = True
                    break
                    
            if not assigned:
                # Créer un nouveau groupe
                factor_groups[factor] = [i]
        
        # Effondrer chaque groupe
        for group_factor, group_indices in factor_groups.items():
            if len(group_indices) < 2:
                continue  # Ignorer les groupes singuliers
                
            # Calculer les poids moyens pour ce groupe
            group_keys = [keys[i] for i in group_indices]
            
            # Sélectionner le chemin avec l'entropie la plus faible (le plus certain)
            entropies = [self.pathway_entropy.get(k, 1.0) for k in group_keys]
            most_certain_idx = entropies.index(min(entropies))
            representative_key = group_keys[most_certain_idx]
            
            # Utiliser le résultat et les poids du représentant
            result, compressed_weights = self.pathway_cache[representative_key]
            
            # Ajouter au registre des chemins effondrés
            self.collapsed_ids.append(representative_key)
            self.collapsed_weights.append(compressed_weights)
            self.collapse_counts.append(1)
            
            # Ajouter au vecteur d'index FAISS pour les recherches futures
            if FAISS_AVAILABLE:
                if representative_key in self.pathway_vectors:
                    vector = self.pathway_vectors[representative_key]
                    if len(self.collapsed_pathways_data) == 0:
                        self.collapsed_pathways_data = vector
                    else:
                        self.collapsed_pathways_data = np.vstack((self.collapsed_pathways_data, vector))
                    self.index.add(vector)
            
            # Enregistrer l'effondrement pour l'historique
            self.collapse_history.append({
                "time": time.time(),
                "group_size": len(group_indices),
                "representative": representative_key[:8],
                "factor": group_factor
            })
            
            # Limiter la taille des chemins effondrés
            if len(self.collapsed_ids) > self.max_collapsed_pathways:
                # Trouver le chemin le moins utilisé
                min_usage_idx = self.collapse_counts.index(min(self.collapse_counts))
                
                # Supprimer ce chemin
                self.collapsed_ids.pop(min_usage_idx)
                self.collapsed_weights.pop(min_usage_idx)
                self.collapse_counts.pop(min_usage_idx)
                
                if FAISS_AVAILABLE and len(self.collapsed_pathways_data) > 0:
                    # Reconstruire l'index FAISS (il n'y a pas de suppression directe)
                    self.collapsed_pathways_data = np.delete(self.collapsed_pathways_data, min_usage_idx, axis=0)
                    self.index = faiss.IndexFlatL2(self.input_dim)
                    if len(self.collapsed_pathways_data) > 0:
                        self.index.add(self.collapsed_pathways_data)
    
    def save_state(self, filename: str = "quantum_memory_state.json"):
        """
        Sauvegarder l'état de la mémoire quantique
        
        Args:
            filename: Nom du fichier de sauvegarde
        """
        save_path = os.path.join(self.save_dir, filename)
        
        # Créer un état serializable
        state = {
            "stats": {
                "total_queries": self.total_queries,
                "cache_hits": self.cache_hits,
                "collapse_hits": self.collapse_hits,
                "avg_query_time": sum(self.query_times) / max(1, len(self.query_times)),
                "collapse_count": len(self.collapse_history),
                "temporal_versions_count": len(self.temporal_versions),
                "concept_drift_detected": self.concept_drift_detected
            },
            "params": {
                "similarity_threshold": self.similarity_threshold,
                "base_similarity_threshold": self.base_similarity_threshold,
                "capacity": self.capacity,
                "collapse_threshold": self.collapse_threshold,
                "max_collapsed_pathways": self.max_collapsed_pathways,
                "d2_params": self.d2_params
            },
            "collapse_history": self.collapse_history[-10:],  # Garder seulement les 10 derniers
            "timestamp": time.time()
        }
        
        # Sauvegarder dans un fichier JSON
        with open(save_path, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.info(f"État de la mémoire quantique sauvegardé dans {save_path}")
        
        return save_path
    
    def load_state(self, filename: str = "quantum_memory_state.json"):
        """
        Charger l'état de la mémoire quantique
        
        Args:
            filename: Nom du fichier de sauvegarde
            
        Returns:
            bool: Succès du chargement
        """
        load_path = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(load_path):
            logger.warning(f"Fichier d'état {load_path} non trouvé")
            return False
        
        try:
            with open(load_path, 'r') as f:
                state = json.load(f)
                
            # Restaurer les paramètres
            self.similarity_threshold = state["params"]["similarity_threshold"]
            self.base_similarity_threshold = state["params"]["base_similarity_threshold"]
            self.capacity = state["params"]["capacity"]
            self.collapse_threshold = state["params"]["collapse_threshold"]
            self.max_collapsed_pathways = state["params"]["max_collapsed_pathways"]
            
            if "d2_params" in state["params"]:
                self.d2_params = state["params"]["d2_params"]
                
            # Restaurer les statistiques
            self.total_queries = state["stats"]["total_queries"]
            self.cache_hits = state["stats"]["cache_hits"]
            self.collapse_hits = state["stats"]["collapse_hits"]
            self.concept_drift_detected = state["stats"]["concept_drift_detected"]
            
            # Restaurer l'historique d'effondrement
            if "collapse_history" in state:
                self.collapse_history = state["collapse_history"]
                
            logger.info(f"État de la mémoire quantique chargé depuis {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'état: {e}")
            return False
    
    def get_statistics(self):
        """
        Obtenir les statistiques du système de mémoire quantique
        
        Returns:
            dict: Statistiques de la mémoire
        """
        avg_query_time = 0
        if len(self.query_times) > 0:
            avg_query_time = sum(self.query_times) / len(self.query_times)
            
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "collapse_hits": self.collapse_hits,
            "cache_hit_rate": (self.cache_hits + self.collapse_hits) / max(1, self.total_queries),
            "average_query_time_ms": avg_query_time * 1000,
            "pathway_cache_size": len(self.pathway_cache),
            "collapsed_pathways_size": len(self.collapsed_ids),
            "similarity_threshold": self.similarity_threshold,
            "concept_drift_detected": self.concept_drift_detected,
            "d2_params": self.d2_params,
            "collapse_history_count": len(self.collapse_history)
        }


# Test du module si exécuté directement
if __name__ == "__main__":
    # Créer une instance de mémoire quantique
    memory = PrimeFactorizedQuantumMemory(
        capacity=500,
        collapse_threshold=20,
        similarity_threshold=0.85,
        input_dim=128,
        d2_integration=True
    )
    
    # Simuler des tenseurs d'entrée et des poids
    def generate_random_tensor(size, seed=None):
        if seed is not None:
            torch.manual_seed(seed)
        return torch.randn(size)
    
    # Fonction de propagation simulée
    def forward_func(x, weights):
        if isinstance(weights, list):
            # Simuler une propagation avec plusieurs couches
            result = x
            for w in weights:
                result = torch.matmul(result, w)
            return result
        else:
            # Simuler une propagation simple
            return torch.matmul(x, weights)
    
    # Tester avec quelques entrées
    print("Test du système de mémoire quantique...")
    
    # Générer des entrées et des poids
    input_dim = 128
    output_dim = 64
    batch_size = 4
    
    inputs = []
    expert_weights = []
    
    for i in range(10):
        # Générer une entrée
        x = generate_random_tensor((batch_size, input_dim), seed=i)
        inputs.append(x)
        
        # Générer des poids (simuler un expert)
        w = generate_random_tensor((input_dim, output_dim), seed=i+100)
        expert_weights.append(w)
    
    # Exécuter plusieurs requêtes
    for i in range(30):
        # Sélectionner une entrée (avec répétition pour tester le cache)
        idx = i % len(inputs)
        x = inputs[idx]
        w = expert_weights[idx]
        
        # Interroger la mémoire
        result, used_weights = memory.query(x, w, forward_func)
        
        # Vérifier si les poids utilisés sont les poids d'expert ou du cache
        is_expert = (used_weights is w)
        status = "Expert" if is_expert else "Cache/Collapsed"
        
        print(f"Requête {i+1}: {status}, Forme du résultat: {result.shape}")
    
    # Afficher les statistiques
    stats = memory.get_statistics()
    print("\nStatistiques de la mémoire quantique:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Sauvegarder l'état
    save_path = memory.save_state()
    print(f"\nÉtat sauvegardé dans: {save_path}")
    
    # Tester l'intégration D2
    memory.set_d2_parameters(activation=0.7, entropy=0.5, stim_level=0.3)
    print("\nParamètres D2 mis à jour:")
    print(f"  {memory.d2_params}")