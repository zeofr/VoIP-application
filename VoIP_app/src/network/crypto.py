from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import base64
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AudioEncryption:
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize audio encryption
        
        Args:
            key: Optional encryption key (generated if None)
        """
        self.key = key or get_random_bytes(32)  # 256-bit key
        self.salt = get_random_bytes(16)
        self.iv = get_random_bytes(16)
        
        # Derive encryption key
        self.derived_key = PBKDF2(
            self.key,
            self.salt,
            dkLen=32,
            count=100000,
            hmac_hash_module=SHA256
        )
        
        logger.info("Initialized audio encryption")
    
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt audio data
        
        Args:
            data: Audio data to encrypt
        
        Returns:
            Tuple of (encrypted_data, iv)
        """
        try:
            # Generate new IV for each packet
            iv = get_random_bytes(16)
            cipher = AES.new(self.derived_key, AES.MODE_CFB, iv)
            encrypted = cipher.encrypt(data)
            return encrypted, iv
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            return b'', b''
    
    def decrypt(self, encrypted_data: bytes, iv: bytes) -> Optional[bytes]:
        """
        Decrypt audio data
        
        Args:
            encrypted_data: Encrypted audio data
            iv: Initialization vector
        
        Returns:
            Optional[bytes]: Decrypted data or None if decryption failed
        """
        try:
            cipher = AES.new(self.derived_key, AES.MODE_CFB, iv)
            decrypted = cipher.decrypt(encrypted_data)
            return decrypted
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return None
    
    def get_key_info(self) -> dict:
        """Get encryption key information"""
        return {
            'key': base64.b64encode(self.key).decode(),
            'salt': base64.b64encode(self.salt).decode(),
            'iv': base64.b64encode(self.iv).decode()
        }
    
    def set_key(self, key: bytes, salt: bytes):
        """
        Set encryption key and salt
        
        Args:
            key: Encryption key
            salt: Key derivation salt
        """
        self.key = key
        self.salt = salt
        self.derived_key = PBKDF2(
            self.key,
            self.salt,
            dkLen=32,
            count=100000,
            hmac_hash_module=SHA256
        )
        logger.info("Updated encryption key") 