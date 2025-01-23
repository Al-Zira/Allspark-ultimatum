# File: src/security_utils.py
import os
import secrets
import hashlib
from cryptography.fernet import Fernet
from base64 import b64encode

class SecurityManager:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def encrypt_sensitive_data(self, data: str) -> bytes:
        """Encrypt sensitive data during processing"""
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_sensitive_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data).decode()

    def secure_file_deletion(self, file_path: str):
        """Securely delete temporary files"""
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                # Multiple pass overwrite
                for _ in range(3):
                    with open(file_path, 'wb') as f:
                        f.write(secrets.token_bytes(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                
                os.remove(file_path)
                
                # Verify deletion
                if os.path.exists(file_path):
                    raise RuntimeError("File deletion failed")
                    
        except Exception as e:
            raise RuntimeError(f"Secure deletion failed: {e}")

    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for logging"""
        salt = secrets.token_bytes(16)
        return b64encode(hashlib.pbkdf2_hmac(
            'sha256', 
            data.encode(), 
            salt, 
            100000
        )).decode()