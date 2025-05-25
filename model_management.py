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
Model Management for NeuronasX

This module provides functionality for managing language models from various
repositories including Ollama, Hugging Face, and GitHub.
"""

import os
import logging
import json
import subprocess
import requests
import threading
import uuid
from datetime import datetime
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages language models from various repositories for the NeuronasX system.
    """
    
    def __init__(self):
        """Initialize the model manager"""
        self.model_cache = {}
        self.download_tasks = {}
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        
        # Create models directory if it doesn't exist
        self.models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Local models metadata file
        self.metadata_file = os.path.join(self.models_dir, "metadata.json")
        self._load_metadata()
    
    def _load_metadata(self):
        """Load model metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.model_cache = json.load(f)
            except Exception as e:
                logger.error(f"Error loading model metadata: {e}")
                self.model_cache = {}
        else:
            self.model_cache = {}
    
    def _save_metadata(self):
        """Save model metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.model_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving model metadata: {e}")
    
    def list_models(self, repository="ollama"):
        """
        List available models from the specified repository
        
        Args:
            repository (str): Repository to list models from
            
        Returns:
            list: Available models
        """
        if repository == "ollama":
            return self._list_ollama_models()
        elif repository == "huggingface":
            return self._list_huggingface_models()
        elif repository == "github":
            return self._list_github_models()
        elif repository == "local":
            return self._list_local_models()
        else:
            logger.error(f"Unknown repository: {repository}")
            return []
    
    def _list_ollama_models(self):
        """List models from Ollama"""
        try:
            # Try to get models from Ollama API
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models_data = response.json()
                models = []
                
                for model in models_data.get('models', []):
                    models.append({
                        "name": model.get('name'),
                        "source": "ollama",
                        "size": model.get('size'),
                        "modified_at": model.get('modified_at')
                    })
                
                return models
            else:
                logger.warning(f"Failed to get models from Ollama: {response.status_code}")
                
                # Return cached models
                models = []
                for name, metadata in self.model_cache.items():
                    if metadata.get('source') == 'ollama':
                        models.append({
                            "name": name,
                            "source": "ollama",
                            "size": metadata.get('size', 'unknown'),
                            "modified_at": metadata.get('modified_at', datetime.utcnow().isoformat())
                        })
                
                return models
                
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            
            # Return simulated models when Ollama is not available
            return [
                {"name": "llama3:8b", "source": "ollama", "size": "4.7GB", "modified_at": "2025-05-01T00:00:00Z"},
                {"name": "mistral:7b", "source": "ollama", "size": "4.1GB", "modified_at": "2025-05-01T00:00:00Z"},
                {"name": "gemma:7b", "source": "ollama", "size": "4.2GB", "modified_at": "2025-05-01T00:00:00Z"},
                {"name": "phi3:3b", "source": "ollama", "size": "1.5GB", "modified_at": "2025-05-01T00:00:00Z"},
                {"name": "nous-hermes2:7b", "source": "ollama", "size": "4.1GB", "modified_at": "2025-05-01T00:00:00Z"}
            ]
    
    def _list_huggingface_models(self):
        """List models from Hugging Face"""
        # Return recommended models for NeuronasX
        models = [
            {"name": "meta-llama/Llama-3-8B", "source": "huggingface", "size": "8B", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "mistralai/Mistral-7B-v0.1", "source": "huggingface", "size": "7B", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "google/gemma-7b", "source": "huggingface", "size": "7B", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "microsoft/phi-3-mini-4k-instruct", "source": "huggingface", "size": "3.8B", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "NousResearch/Nous-Hermes-2-Yi-34B", "source": "huggingface", "size": "34B", "modified_at": "2025-05-01T00:00:00Z"}
        ]
        
        # Add cached models
        for name, metadata in self.model_cache.items():
            if metadata.get('source') == 'huggingface' and not any(m['name'] == name for m in models):
                models.append({
                    "name": name,
                    "source": "huggingface",
                    "size": metadata.get('size', 'unknown'),
                    "modified_at": metadata.get('modified_at', datetime.utcnow().isoformat())
                })
        
        return models
    
    def _list_github_models(self):
        """List models from GitHub"""
        # Return recommended models for NeuronasX
        models = [
            {"name": "ggerganov/llama.cpp", "source": "github", "size": "varies", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "microsoft/phi", "source": "github", "size": "varies", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "nomic-ai/gpt4all", "source": "github", "size": "varies", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "TheBloke/Llama-3-Instruct-8B-GGUF", "source": "github", "size": "varies", "modified_at": "2025-05-01T00:00:00Z"},
            {"name": "THUDM/ChatGLM3", "source": "github", "size": "varies", "modified_at": "2025-05-01T00:00:00Z"}
        ]
        
        # Add cached models
        for name, metadata in self.model_cache.items():
            if metadata.get('source') == 'github' and not any(m['name'] == name for m in models):
                models.append({
                    "name": name,
                    "source": "github",
                    "size": metadata.get('size', 'unknown'),
                    "modified_at": metadata.get('modified_at', datetime.utcnow().isoformat())
                })
        
        return models
    
    def _list_local_models(self):
        """List locally available models"""
        models = []
        
        # List models from cache
        for name, metadata in self.model_cache.items():
            if metadata.get('local_path'):
                models.append({
                    "name": name,
                    "source": metadata.get('source', 'local'),
                    "size": metadata.get('size', 'unknown'),
                    "modified_at": metadata.get('modified_at', datetime.utcnow().isoformat()),
                    "local_path": metadata.get('local_path')
                })
        
        return models
    
    def download_model(self, model_name, repository="ollama"):
        """
        Download a model from the specified repository
        
        Args:
            model_name (str): Name of the model to download
            repository (str): Repository to download from
            
        Returns:
            dict: Download task information
        """
        # Generate a task ID
        task_id = str(uuid.uuid4())
        
        # Create task info
        task_info = {
            "task_id": task_id,
            "model_name": model_name,
            "repository": repository,
            "status": "starting",
            "progress": 0,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "error": None
        }
        
        # Store task info
        self.download_tasks[task_id] = task_info
        
        # Start download in a separate thread
        thread = threading.Thread(
            target=self._download_model_thread,
            args=(task_id, model_name, repository)
        )
        thread.daemon = True
        thread.start()
        
        return task_info
    
    def _download_model_thread(self, task_id, model_name, repository):
        """
        Background thread for downloading a model
        
        Args:
            task_id (str): Task ID
            model_name (str): Name of the model to download
            repository (str): Repository to download from
        """
        task_info = self.download_tasks[task_id]
        task_info["status"] = "downloading"
        
        try:
            if repository == "ollama":
                self._download_ollama_model(task_id, model_name)
            elif repository == "huggingface":
                self._download_huggingface_model(task_id, model_name)
            elif repository == "github":
                self._download_github_model(task_id, model_name)
            else:
                raise ValueError(f"Unknown repository: {repository}")
                
            # Update task info
            task_info["status"] = "completed"
            task_info["progress"] = 100
            task_info["end_time"] = datetime.utcnow().isoformat()
            
            # Update model cache
            self.model_cache[model_name] = {
                "source": repository,
                "downloaded_at": datetime.utcnow().isoformat(),
                "modified_at": datetime.utcnow().isoformat(),
                "size": "unknown"
            }
            
            # Save metadata
            self._save_metadata()
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name} from {repository}: {e}")
            
            # Update task info
            task_info["status"] = "failed"
            task_info["error"] = str(e)
            task_info["end_time"] = datetime.utcnow().isoformat()
    
    def _download_ollama_model(self, task_id, model_name):
        """
        Download a model from Ollama
        
        Args:
            task_id (str): Task ID
            model_name (str): Name of the model to download
        """
        task_info = self.download_tasks[task_id]
        
        try:
            # Pull model using Ollama CLI
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor progress
            progress = 0
            for line in iter(process.stdout.readline, ''):
                # Try to extract progress information
                if "pulling" in line.lower() and "%" in line:
                    try:
                        progress_str = line.split("%")[0].split()[-1]
                        progress = int(float(progress_str))
                    except (ValueError, IndexError):
                        pass
                
                # Update task info
                task_info["progress"] = progress
                
                # Log progress
                logger.info(f"Ollama pull {model_name}: {line.strip()}")
                
            # Wait for process to complete
            process.stdout.close()
            return_code = process.wait()
            
            if return_code != 0:
                error = process.stderr.read()
                raise Exception(f"Ollama pull failed with code {return_code}: {error}")
                
        except FileNotFoundError:
            # Ollama CLI not found, try using API
            logger.warning("Ollama CLI not found, trying API")
            
            # Start model pull using Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to start model pull: {response.status_code} {response.text}")
                
            # API doesn't provide progress information, so we just have to wait
            task_info["progress"] = 50
            logger.info(f"Started pull for {model_name} using Ollama API")
    
    def _download_huggingface_model(self, task_id, model_name):
        """
        Download a model from Hugging Face
        
        Args:
            task_id (str): Task ID
            model_name (str): Name of the model to download
        """
        task_info = self.download_tasks[task_id]
        
        # Create model directory
        model_dir = os.path.join(self.models_dir, "huggingface", model_name.replace("/", "_"))
        os.makedirs(model_dir, exist_ok=True)
        
        # Update model cache with local path
        self.model_cache[model_name] = {
            "source": "huggingface",
            "downloaded_at": datetime.utcnow().isoformat(),
            "modified_at": datetime.utcnow().isoformat(),
            "size": "unknown",
            "local_path": model_dir
        }
        
        # Download model info (but not the actual model)
        try:
            # Get model info from Hugging Face API
            response = requests.get(
                f"https://huggingface.co/api/models/{model_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                model_info = response.json()
                
                # Save model info
                with open(os.path.join(model_dir, "model_info.json"), 'w') as f:
                    json.dump(model_info, f, indent=2)
                    
                # Update model cache with more information
                self.model_cache[model_name]["size"] = f"{model_info.get('params', 0):,}"
                self.model_cache[model_name]["modified_at"] = model_info.get('last_modified', datetime.utcnow().isoformat())
                
                # Save metadata
                self._save_metadata()
                
            task_info["progress"] = 100
            
        except Exception as e:
            logger.error(f"Error downloading model info for {model_name}: {e}")
            task_info["progress"] = 100  # Mark as complete anyway
    
    def _download_github_model(self, task_id, model_name):
        """
        Download a model from GitHub
        
        Args:
            task_id (str): Task ID
            model_name (str): Name of the model to download
        """
        task_info = self.download_tasks[task_id]
        
        # Create model directory
        model_dir = os.path.join(self.models_dir, "github", model_name.replace("/", "_"))
        os.makedirs(model_dir, exist_ok=True)
        
        # Update model cache with local path
        self.model_cache[model_name] = {
            "source": "github",
            "downloaded_at": datetime.utcnow().isoformat(),
            "modified_at": datetime.utcnow().isoformat(),
            "size": "unknown",
            "local_path": model_dir
        }
        
        # Download model info (but not the actual model)
        try:
            # Get repo info from GitHub API
            response = requests.get(
                f"https://api.github.com/repos/{model_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                repo_info = response.json()
                
                # Save repo info
                with open(os.path.join(model_dir, "repo_info.json"), 'w') as f:
                    json.dump(repo_info, f, indent=2)
                    
                # Update model cache with more information
                self.model_cache[model_name]["modified_at"] = repo_info.get('updated_at', datetime.utcnow().isoformat())
                self.model_cache[model_name]["size"] = f"{repo_info.get('size', 0):,} KB"
                
                # Save metadata
                self._save_metadata()
                
            task_info["progress"] = 100
            
        except Exception as e:
            logger.error(f"Error downloading repo info for {model_name}: {e}")
            task_info["progress"] = 100  # Mark as complete anyway
    
    def get_download_status(self, task_id):
        """
        Get the status of a download task
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task information
        """
        return self.download_tasks.get(task_id)
    
    def delete_model(self, model_name, repository="ollama"):
        """
        Delete a model
        
        Args:
            model_name (str): Name of the model to delete
            repository (str): Repository the model is from
            
        Returns:
            bool: Success status
        """
        try:
            if repository == "ollama":
                return self._delete_ollama_model(model_name)
            elif repository == "huggingface":
                return self._delete_huggingface_model(model_name)
            elif repository == "github":
                return self._delete_github_model(model_name)
            elif repository == "local":
                return self._delete_local_model(model_name)
            else:
                logger.error(f"Unknown repository: {repository}")
                return False
        except Exception as e:
            logger.error(f"Error deleting model {model_name} from {repository}: {e}")
            return False
    
    def _delete_ollama_model(self, model_name):
        """
        Delete a model from Ollama
        
        Args:
            model_name (str): Name of the model to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Delete model using Ollama CLI
            process = subprocess.run(
                ["ollama", "rm", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                logger.error(f"Error deleting model {model_name}: {process.stderr}")
                
                # Try using API
                logger.info("Trying to delete model using API")
                response = requests.delete(
                    f"{self.ollama_url}/api/delete",
                    json={"name": model_name},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to delete model using API: {response.status_code} {response.text}")
                    return False
            
            # Remove from cache
            if model_name in self.model_cache:
                del self.model_cache[model_name]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Ollama model {model_name}: {e}")
            return False
    
    def _delete_huggingface_model(self, model_name):
        """
        Delete a model from Hugging Face
        
        Args:
            model_name (str): Name of the model to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Get model info from cache
            model_info = self.model_cache.get(model_name)
            
            if model_info and 'local_path' in model_info:
                # Delete local files
                import shutil
                shutil.rmtree(model_info['local_path'], ignore_errors=True)
            
            # Remove from cache
            if model_name in self.model_cache:
                del self.model_cache[model_name]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Hugging Face model {model_name}: {e}")
            return False
    
    def _delete_github_model(self, model_name):
        """
        Delete a model from GitHub
        
        Args:
            model_name (str): Name of the model to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Get model info from cache
            model_info = self.model_cache.get(model_name)
            
            if model_info and 'local_path' in model_info:
                # Delete local files
                import shutil
                shutil.rmtree(model_info['local_path'], ignore_errors=True)
            
            # Remove from cache
            if model_name in self.model_cache:
                del self.model_cache[model_name]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting GitHub model {model_name}: {e}")
            return False
    
    def _delete_local_model(self, model_name):
        """
        Delete a local model
        
        Args:
            model_name (str): Name of the model to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Get model info from cache
            model_info = self.model_cache.get(model_name)
            
            if model_info and 'local_path' in model_info:
                # Delete local files
                import shutil
                shutil.rmtree(model_info['local_path'], ignore_errors=True)
            
            # Remove from cache
            if model_name in self.model_cache:
                del self.model_cache[model_name]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting local model {model_name}: {e}")
            return False