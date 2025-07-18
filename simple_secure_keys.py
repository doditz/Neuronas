"""
Simple and Secure API Key Management for Neuronas
================================================

Lightweight, Python-native secure key handling without external dependencies.
Better alternative to .NET for this use case.
"""

import os
import json
import hashlib
import getpass
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from base64 import b64encode, b64decode

logger = logging.getLogger(__name__)

class SimpleSecureKeys:
    """
    Simple, secure API key management using Python standard library only
    """
    
    def __init__(self):
        """Initialize simple secure key manager"""
        self.config_dir = Path.home() / ".neuronas"
        self.config_dir.mkdir(exist_ok=True)
        self.keys_file = self.config_dir / "api_keys.json"
        
        # Set secure permissions on config directory
        if os.name != 'nt':  # Not Windows
            os.chmod(self.config_dir, 0o700)
    
    def _simple_encrypt(self, text: str, password: str) -> str:
        """Simple XOR encryption (better than plaintext)"""
        key = hashlib.sha256(password.encode()).digest()
        encrypted = bytearray()
        
        for i, char in enumerate(text.encode()):
            encrypted.append(char ^ key[i % len(key)])
        
        return b64encode(encrypted).decode()
    
    def _simple_decrypt(self, encrypted_text: str, password: str) -> str:
        """Simple XOR decryption"""
        key = hashlib.sha256(password.encode()).digest()
        encrypted = b64decode(encrypted_text.encode())
        decrypted = bytearray()
        
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key[i % len(key)])
        
        return decrypted.decode()
    
    def store_key(self, service: str, api_key: str, overwrite: bool = None) -> bool:
        """
        Store API key securely with interactive overwrite handling
        
        Args:
            service: Service name (e.g., 'perplexity', 'openai')
            api_key: The API key to store
            overwrite: Whether to overwrite existing key (None = ask user)
            
        Returns:
            bool: Success status
        """
        try:
            # Load existing keys
            keys_data = self._load_keys()
            
            # Check if key already exists and handle overwrite
            if service in keys_data:
                if overwrite is None:
                    # Ask user interactively
                    existing_date = keys_data[service].get('stored_at', 'unknown date')
                    print(f"\n🔑 API key for {service.title()} already exists (stored: {existing_date})")
                    
                    while True:
                        choice = input("Do you want to update it? (y/n): ").lower().strip()
                        if choice in ['y', 'yes']:
                            overwrite = True
                            break
                        elif choice in ['n', 'no']:
                            print(f"⚠️ Keeping existing {service} key unchanged")
                            return False
                        else:
                            print("Please enter 'y' for yes or 'n' for no")
                elif not overwrite:
                    print(f"⚠️ Key for {service} already exists. Use overwrite=True to replace.")
                    return False
            
            # Get master password
            if not hasattr(self, '_master_password'):
                self._master_password = getpass.getpass(
                    f"Enter master password for {service} key storage: "
                )
            
            # Encrypt and store
            encrypted_key = self._simple_encrypt(api_key, self._master_password)
            
            keys_data[service] = {
                'encrypted_key': encrypted_key,
                'key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:16],  # First 16 chars for validation
                'stored_at': str(datetime.now())
            }
            
            # Save to file
            self._save_keys(keys_data)
            
            action = "updated" if service in self._load_keys() else "stored"
            print(f"✅ API key for {service} {action} securely")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store key for {service}: {e}")
            return False
    
    def get_key(self, service: str) -> Optional[str]:
        """
        Retrieve API key
        
        Args:
            service: Service name
            
        Returns:
            str: Decrypted API key or None
        """
        try:
            # First try environment variable
            env_var = f"{service.upper()}_API_KEY"
            env_key = os.getenv(env_var)
            if env_key:
                logger.debug(f"✅ Retrieved {service} key from environment")
                return env_key
            
            # Try encrypted storage
            keys_data = self._load_keys()
            
            if service not in keys_data:
                logger.warning(f"⚠️ No stored key found for {service}")
                return None
            
            # Get master password if not cached
            if not hasattr(self, '_master_password'):
                self._master_password = getpass.getpass(
                    f"Enter master password to decrypt {service} key: "
                )
            
            # Decrypt key
            encrypted_key = keys_data[service]['encrypted_key']
            api_key = self._simple_decrypt(encrypted_key, self._master_password)
            
            # Validate key integrity
            stored_hash = keys_data[service]['key_hash']
            current_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            
            if stored_hash != current_hash:
                logger.error(f"❌ Key integrity check failed for {service}")
                return None
            
            logger.debug(f"✅ Retrieved {service} key from secure storage")
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve key for {service}: {e}")
            return None
    
    def _load_keys(self) -> Dict[str, Any]:
        """Load keys from file"""
        if not self.keys_file.exists():
            return {}
        
        try:
            with open(self.keys_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load keys file: {e}")
            return {}
    
    def _save_keys(self, keys_data: Dict[str, Any]) -> None:
        """Save keys to file with secure permissions"""
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(keys_data, f, indent=2)
            
            # Set secure file permissions (owner read/write only)
            if os.name != 'nt':  # Not Windows
                os.chmod(self.keys_file, 0o600)
                
        except Exception as e:
            logger.error(f"Failed to save keys file: {e}")
    
    def list_services(self) -> list:
        """List all services with stored keys"""
        keys_data = self._load_keys()
        return list(keys_data.keys())
    
    def delete_key(self, service: str) -> bool:
        """Delete a stored key"""
        try:
            keys_data = self._load_keys()
            
            if service in keys_data:
                del keys_data[service]
                self._save_keys(keys_data)
                print(f"✅ Deleted key for {service}")
                return True
            else:
                print(f"⚠️ No key found for {service}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete key for {service}: {e}")
            return False


class EnvKeyHelper:
    """
    Helper for environment variable key management
    """
    
    @staticmethod
    def setup_env_keys():
        """Interactive setup for environment variables"""
        services = {
            'perplexity': 'PERPLEXITY_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        
        print("🔧 Environment Variable Setup")
        print("=" * 40)
        
        for service, env_var in services.items():
            current_value = os.getenv(env_var)
            
            if current_value:
                print(f"✅ {env_var}: Already set")
            else:
                print(f"❌ {env_var}: Not set")
                
                choice = input(f"Set {env_var} now? (y/n): ").lower()
                if choice == 'y':
                    api_key = getpass.getpass(f"Enter {service} API key: ")
                    
                    if api_key:
                        # Add to current session
                        os.environ[env_var] = api_key
                        
                        # Add to shell config
                        EnvKeyHelper.add_to_shell_config(env_var, api_key)
                        print(f"✅ {env_var} configured")
    
    @staticmethod
    def add_to_shell_config(env_var: str, value: str):
        """Add environment variable to shell configuration"""
        shell_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile"
        ]
        
        for shell_file in shell_files:
            if shell_file.exists():
                # Check if already exists
                content = shell_file.read_text()
                if f"export {env_var}=" not in content:
                    with open(shell_file, 'a') as f:
                        f.write(f'\n# Neuronas API Key\nexport {env_var}="{value}"\n')
                    print(f"✅ Added {env_var} to {shell_file}")
                break
    
    @staticmethod
    def validate_keys():
        """Validate that required keys are available"""
        required_keys = [
            'PERPLEXITY_API_KEY',
            'OPENAI_API_KEY'  # Add others as needed
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"⚠️ Missing required API keys: {', '.join(missing_keys)}")
            return False
        else:
            print("✅ All required API keys are configured")
            return True


# Integration with Neuronas
class NeuronasKeyManager:
    """
    Unified key manager for Neuronas system
    """
    
    def __init__(self):
        """Initialize Neuronas key manager"""
        self.simple_keys = SimpleSecureKeys()
        self.env_helper = EnvKeyHelper()
    
    def get_api_key(self, service: str, interactive: bool = True) -> Optional[str]:
        """
        Get API key with fallback chain and interactive setup
        
        Args:
            service: Service name
            interactive: Whether to prompt user for missing keys
            
        Returns:
            str: API key or None
        """
        # Try environment first (fastest)
        env_var = f"{service.upper()}_API_KEY"
        key = os.getenv(env_var)
        if key:
            print(f"✅ Using {service} key from environment variable")
            return key
        
        # Try secure storage
        key = self.simple_keys.get_key(service)
        if key:
            print(f"✅ Using {service} key from secure storage")
            return key
        
        # If not found and interactive mode, offer to set it up
        if interactive:
            print(f"\n🔑 No API key found for {service.title()}")
            
            while True:
                choice = input(f"Would you like to set up {service.title()} API key now? (y/n): ").lower().strip()
                if choice in ['y', 'yes']:
                    api_key = getpass.getpass(f"Enter {service.title()} API key: ")
                    if api_key:
                        # Store in secure storage
                        success = self.simple_keys.store_key(service, api_key)
                        if success:
                            print(f"✅ {service.title()} API key configured successfully!")
                            return api_key
                        else:
                            print(f"❌ Failed to store {service} API key")
                    else:
                        print("❌ No key entered")
                    break
                elif choice in ['n', 'no']:
                    print(f"⚠️ Skipping {service.title()} API key setup")
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no")
        
        return None
    
    def setup_all_keys(self):
        """Interactive setup for all keys"""
        print("🔐 Neuronas API Key Setup")
        print("=" * 30)
        
        # Check environment variables
        self.env_helper.setup_env_keys()
        
        print("\n📋 Current Status:")
        services = ['perplexity', 'openai', 'anthropic', 'google']
        
        for service in services:
            key = self.get_api_key(service)
            if key:
                print(f"✅ {service.title()}: Configured")
            else:
                print(f"❌ {service.title()}: Not configured")


# Command-line interface
def main():
    """Main CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Neuronas Secure Key Manager")
        print("Usage:")
        print("  python secure_key_manager.py setup    - Interactive setup")
        print("  python secure_key_manager.py store <service> - Store a key")
        print("  python secure_key_manager.py get <service>   - Get a key")
        print("  python secure_key_manager.py list           - List services")
        print("  python secure_key_manager.py validate       - Validate keys")
        return
    
    action = sys.argv[1]
    key_manager = NeuronasKeyManager()
    
    if action == "setup":
        key_manager.setup_all_keys()
    
    elif action == "store" and len(sys.argv) > 2:
        service = sys.argv[2]
        api_key = getpass.getpass(f"Enter API key for {service}: ")
        key_manager.simple_keys.store_key(service, api_key)
    
    elif action == "get" and len(sys.argv) > 2:
        service = sys.argv[2]
        key = key_manager.get_api_key(service)
        if key:
            print(f"✅ Key found for {service} (length: {len(key)})")
        else:
            print(f"❌ No key found for {service}")
    
    elif action == "list":
        services = key_manager.simple_keys.list_services()
        print("📋 Stored services:", ", ".join(services))
    
    elif action == "validate":
        key_manager.env_helper.validate_keys()
    
    else:
        print("❌ Invalid action or missing parameters")


if __name__ == "__main__":
    from datetime import datetime
    main()
