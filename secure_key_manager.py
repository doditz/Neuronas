"""
Secure API Key Management for Neuronas
=====================================

This module provides multiple secure methods for handling API keys
without requiring .NET dependencies.
"""

import os
import json
import base64
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class SecureKeyManager:
    """
    Secure API key management with multiple security layers
    """
    
    def __init__(self, master_password: Optional[str] = None):
        """
        Initialize secure key manager
        
        Args:
            master_password: Optional master password for encryption
        """
        self.master_password = master_password
        self._key_cache = {}
        self.config_dir = Path.home() / ".neuronas" / "secure"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Secure file paths
        self.encrypted_keys_file = self.config_dir / "keys.enc"
        self.key_hash_file = self.config_dir / "key_hashes.json"
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _get_or_create_salt(self) -> bytes:
        """Get or create salt for key derivation"""
        salt_file = self.config_dir / "salt"
        
        if salt_file.exists():
            return salt_file.read_bytes()
        else:
            salt = os.urandom(16)
            salt_file.write_bytes(salt)
            salt_file.chmod(0o600)  # Read-write for owner only
            return salt
    
    def store_api_key(self, service_name: str, api_key: str, 
                      description: str = "", tags: list = None) -> bool:
        """
        Securely store an API key
        
        Args:
            service_name: Name of the service (e.g., 'perplexity', 'openai')
            api_key: The API key to store
            description: Optional description
            tags: Optional tags for categorization
            
        Returns:
            bool: Success status
        """
        try:
            # Get master password if not provided
            if not self.master_password:
                self.master_password = self._prompt_master_password()
            
            # Load existing keys or create new structure
            keys_data = self._load_encrypted_keys()
            
            # Store key metadata (non-sensitive)
            metadata = {
                'description': description,
                'tags': tags or [],
                'created_at': str(datetime.now()),
                'last_used': None,
                'usage_count': 0
            }
            
            # Encrypt and store the API key
            keys_data[service_name] = {
                'encrypted_key': self._encrypt_key(api_key),
                'metadata': metadata
            }
            
            # Save encrypted keys
            self._save_encrypted_keys(keys_data)
            
            # Store key hash for validation (without exposing the key)
            self._store_key_hash(service_name, api_key)
            
            logger.info(f"✅ API key for {service_name} stored securely")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store API key for {service_name}: {e}")
            return False
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """
        Retrieve an API key securely
        
        Args:
            service_name: Name of the service
            
        Returns:
            str: Decrypted API key or None if not found
        """
        try:
            # Check cache first (for current session)
            if service_name in self._key_cache:
                return self._key_cache[service_name]
            
            # Get master password if not provided
            if not self.master_password:
                self.master_password = self._prompt_master_password()
            
            # Load encrypted keys
            keys_data = self._load_encrypted_keys()
            
            if service_name not in keys_data:
                logger.warning(f"⚠️ No API key found for {service_name}")
                return None
            
            # Decrypt the key
            encrypted_key = keys_data[service_name]['encrypted_key']
            api_key = self._decrypt_key(encrypted_key)
            
            # Update usage metadata
            keys_data[service_name]['metadata']['last_used'] = str(datetime.now())
            keys_data[service_name]['metadata']['usage_count'] += 1
            self._save_encrypted_keys(keys_data)
            
            # Cache for current session
            self._key_cache[service_name] = api_key
            
            logger.debug(f"✅ Retrieved API key for {service_name}")
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve API key for {service_name}: {e}")
            return None
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key"""
        salt = self._get_or_create_salt()
        key = self._derive_key(self.master_password, salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        salt = self._get_or_create_salt()
        key = self._derive_key(self.master_password, salt)
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_key.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def _load_encrypted_keys(self) -> Dict[str, Any]:
        """Load encrypted keys from file"""
        if not self.encrypted_keys_file.exists():
            return {}
        
        try:
            with open(self.encrypted_keys_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load encrypted keys: {e}")
            return {}
    
    def _save_encrypted_keys(self, keys_data: Dict[str, Any]) -> None:
        """Save encrypted keys to file"""
        try:
            with open(self.encrypted_keys_file, 'w') as f:
                json.dump(keys_data, f, indent=2)
            
            # Set secure file permissions
            self.encrypted_keys_file.chmod(0o600)
            
        except Exception as e:
            logger.error(f"Failed to save encrypted keys: {e}")
    
    def _store_key_hash(self, service_name: str, api_key: str) -> None:
        """Store hash of API key for validation"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        hashes_data = {}
        if self.key_hash_file.exists():
            try:
                with open(self.key_hash_file, 'r') as f:
                    hashes_data = json.load(f)
            except:
                pass
        
        hashes_data[service_name] = key_hash
        
        with open(self.key_hash_file, 'w') as f:
            json.dump(hashes_data, f)
        
        self.key_hash_file.chmod(0o600)
    
    def _prompt_master_password(self) -> str:
        """Prompt for master password securely"""
        import getpass
        return getpass.getpass("Enter master password for Neuronas key storage: ")
    
    def list_stored_keys(self) -> Dict[str, Dict]:
        """List all stored keys (metadata only, not the actual keys)"""
        keys_data = self._load_encrypted_keys()
        
        result = {}
        for service_name, data in keys_data.items():
            result[service_name] = data.get('metadata', {})
        
        return result
    
    def delete_api_key(self, service_name: str) -> bool:
        """Delete an API key"""
        try:
            keys_data = self._load_encrypted_keys()
            
            if service_name in keys_data:
                del keys_data[service_name]
                self._save_encrypted_keys(keys_data)
                
                # Remove from cache
                if service_name in self._key_cache:
                    del self._key_cache[service_name]
                
                logger.info(f"✅ Deleted API key for {service_name}")
                return True
            else:
                logger.warning(f"⚠️ No API key found for {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete API key for {service_name}: {e}")
            return False


class EnvironmentKeyManager:
    """
    Enhanced environment variable manager with security features
    """
    
    @staticmethod
    def get_secure_env_key(key_name: str, required: bool = True) -> Optional[str]:
        """
        Get environment variable with security validation
        
        Args:
            key_name: Environment variable name
            required: Whether the key is required
            
        Returns:
            str: Environment variable value or None
        """
        value = os.getenv(key_name)
        
        if not value and required:
            logger.error(f"❌ Required environment variable {key_name} not found")
            return None
        
        # Validate key format (basic checks)
        if value and key_name.endswith('_API_KEY'):
            if len(value) < 10:
                logger.warning(f"⚠️ API key for {key_name} seems too short")
            elif value.startswith('sk-') and len(value) < 40:
                logger.warning(f"⚠️ OpenAI-style key for {key_name} seems incomplete")
        
        if value:
            logger.debug(f"✅ Retrieved {key_name} from environment")
        
        return value
    
    @staticmethod
    def set_env_key_securely(key_name: str, key_value: str, persist: bool = True) -> bool:
        """
        Set environment variable securely
        
        Args:
            key_name: Environment variable name
            key_value: Environment variable value
            persist: Whether to persist to shell config
            
        Returns:
            bool: Success status
        """
        try:
            # Set for current session
            os.environ[key_name] = key_value
            
            if persist:
                # Add to .bashrc or .zshrc
                shell_config = Path.home() / ".bashrc"
                if not shell_config.exists():
                    shell_config = Path.home() / ".zshrc"
                
                if shell_config.exists():
                    # Check if already exists
                    content = shell_config.read_text()
                    if f"export {key_name}=" not in content:
                        with open(shell_config, 'a') as f:
                            f.write(f'\n# Neuronas API Key\nexport {key_name}="{key_value}"\n')
                        
                        logger.info(f"✅ Added {key_name} to {shell_config}")
                    else:
                        logger.info(f"✅ {key_name} already exists in {shell_config}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set {key_name}: {e}")
            return False


class NeuronasKeyVault:
    """
    Unified key management for Neuronas system
    """
    
    def __init__(self, use_encryption: bool = True):
        """
        Initialize Neuronas key vault
        
        Args:
            use_encryption: Whether to use encrypted storage
        """
        self.use_encryption = use_encryption
        self.secure_manager = SecureKeyManager() if use_encryption else None
        self.env_manager = EnvironmentKeyManager()
        
    def get_api_key(self, service: str, fallback_env_var: str = None) -> Optional[str]:
        """
        Get API key with fallback chain: encrypted storage -> environment -> prompt
        
        Args:
            service: Service name (e.g., 'perplexity', 'openai')
            fallback_env_var: Environment variable name as fallback
            
        Returns:
            str: API key or None
        """
        # Try encrypted storage first
        if self.use_encryption and self.secure_manager:
            key = self.secure_manager.get_api_key(service)
            if key:
                return key
        
        # Try environment variable
        if fallback_env_var:
            key = self.env_manager.get_secure_env_key(fallback_env_var, required=False)
            if key:
                return key
        
        # Try standard environment variable pattern
        standard_env_var = f"{service.upper()}_API_KEY"
        key = self.env_manager.get_secure_env_key(standard_env_var, required=False)
        if key:
            return key
        
        logger.warning(f"⚠️ No API key found for {service}")
        return None
    
    def store_api_key(self, service: str, api_key: str, 
                      persist_to_env: bool = False) -> bool:
        """
        Store API key using preferred method
        
        Args:
            service: Service name
            api_key: API key to store
            persist_to_env: Whether to also store in environment
            
        Returns:
            bool: Success status
        """
        success = True
        
        # Store in encrypted storage
        if self.use_encryption and self.secure_manager:
            success &= self.secure_manager.store_api_key(service, api_key)
        
        # Store in environment if requested
        if persist_to_env:
            env_var = f"{service.upper()}_API_KEY"
            success &= self.env_manager.set_env_key_securely(env_var, api_key)
        
        return success


# Integration with existing Neuronas system
def setup_neuronas_key_management():
    """Setup secure key management for Neuronas"""
    from datetime import datetime
    
    # Initialize key vault
    key_vault = NeuronasKeyVault(use_encryption=True)
    
    # Check for existing keys
    services = ['perplexity', 'openai', 'anthropic', 'google']
    
    print("🔐 Neuronas Secure Key Management Setup")
    print("=" * 50)
    
    for service in services:
        key = key_vault.get_api_key(service)
        if key:
            print(f"✅ {service.title()} API key: Configured")
        else:
            print(f"⚠️  {service.title()} API key: Not found")
    
    return key_vault


# CLI interface for key management
def key_management_cli():
    """Command-line interface for key management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Neuronas Secure Key Management")
    parser.add_argument('action', choices=['store', 'get', 'list', 'delete'])
    parser.add_argument('--service', required=True, help='Service name')
    parser.add_argument('--key', help='API key (for store action)')
    parser.add_argument('--env', action='store_true', help='Also store in environment')
    
    args = parser.parse_args()
    
    key_vault = NeuronasKeyVault()
    
    if args.action == 'store':
        if not args.key:
            print("❌ --key required for store action")
            return
        
        success = key_vault.store_api_key(args.service, args.key, args.env)
        if success:
            print(f"✅ Stored API key for {args.service}")
        else:
            print(f"❌ Failed to store API key for {args.service}")
    
    elif args.action == 'get':
        key = key_vault.get_api_key(args.service)
        if key:
            print(f"✅ API key found (length: {len(key)})")
            # Don't print the actual key for security
        else:
            print(f"❌ No API key found for {args.service}")
    
    elif args.action == 'list':
        if key_vault.secure_manager:
            keys = key_vault.secure_manager.list_stored_keys()
            print("📋 Stored API Keys:")
            for service, metadata in keys.items():
                print(f"  {service}: {metadata.get('description', 'No description')}")
        else:
            print("⚠️ Encrypted storage not available")
    
    elif args.action == 'delete':
        if key_vault.secure_manager:
            success = key_vault.secure_manager.delete_api_key(args.service)
            if success:
                print(f"✅ Deleted API key for {args.service}")
            else:
                print(f"❌ Failed to delete API key for {args.service}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        key_management_cli()
    else:
        setup_neuronas_key_management()
