"""crypto.py - Cryptographic utilities for the application."""

import os
import base64
import logging
import hashlib
import hmac
from typing import Union, Optional
from pathlib import Path

from cryptography.fernet import Fernet
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Path to store development key
DEV_KEY_PATH = Path.home() / ".zk_caller_verification" / "dev_key.txt"

# Fernet cipher for symmetric encryption
_fernet = None

def get_fernet():
    """Get a Fernet instance for encryption/decryption.
    
    Uses environment variable FERNET_KEY if available,
    otherwise looks for a saved development key.
    If no key exists, generates a new key for development.
    
    Returns:
        Fernet: Fernet instance for encryption/decryption
    """
    # Try to get key from environment
    key = os.environ.get("FERNET_KEY")
    
    if not key:
        # Check if we have a saved development key
        if DEV_KEY_PATH.exists():
            try:
                with open(DEV_KEY_PATH, "r") as f:
                    key = f.read().strip()
                logger.info("Using saved development key from file")
            except Exception as e:
                logger.error(f"Error reading saved key: {e}")
                # Fall through to key generation
    
    if not key:
        # Generate a new key for development
        key = Fernet.generate_key().decode()
        logger.warning("FERNET_KEY not found in environment, generating one for development...")
        logger.warning(f"Generated key: {key} - In production, set this in environment")
        
        # Save the key for future use
        try:
            # Create directory if it doesn't exist
            DEV_KEY_PATH.parent.mkdir(exist_ok=True, parents=True)
            
            # Save the key
            with open(DEV_KEY_PATH, "w") as f:
                f.write(key)
            logger.info(f"Saved development key to {DEV_KEY_PATH}")
        except Exception as e:
            logger.error(f"Error saving development key: {e}")
    
    # Return a Fernet instance using the key
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt(data: Union[str, bytes, int]) -> str:
    """Encrypt data and return as string.
    
    Args:
        data: Data to encrypt (string, bytes, or integer)
        
    Returns:
        str: Encrypted data as string
    """
    # Convert data to bytes
    if isinstance(data, int):
        data = str(data)
    if isinstance(data, str):
        data = data.encode()
        
    # Encrypt and return as string
    return get_fernet().encrypt(data).decode()

def decrypt(token: str) -> str:
    """Decrypt token and return as string.
    
    Args:
        token: Encrypted token
        
    Returns:
        str: Decrypted data as string
    """
    return get_fernet().decrypt(token.encode()).decode()

def generate_numeric_hash(text: str, length: int = 4) -> int:
    """Generate a numeric hash of the specified length from text.
    
    Args:
        text: Text to hash
        length: Length of the numeric hash (default: 4 digits)
        
    Returns:
        int: Numeric hash
    """
    # Convert to bytes if it's a string
    if isinstance(text, str):
        text = text.encode()
    
    # Generate SHA-256 hash and take first 'length' digits
    hash_obj = hashlib.sha256(text)
    hash_hex = hash_obj.hexdigest()
    
    # Convert first 'length' characters of hash to number
    numeric = int(hash_hex[:length], 16) % (10 ** length)
    
    return numeric

def generate_totp(seed: int, 
                 org_id: int, 
                 rep_id_numeric: int, 
                 time_window: int, 
                 digits: int = 6) -> str:
    """Generate Time-based One-Time Password.
    
    Args:
        seed: Secret seed value
        org_id: Organization ID
        rep_id_numeric: Numeric representation of agent ID
        time_window: Current time window
        digits: Number of digits in the OTP
        
    Returns:
        str: Generated OTP code
    """
    # Convert parameters to bytes
    seed_bytes = seed.to_bytes((seed.bit_length() + 7) // 8, "big")
    
    # Build message: org_id(1B) ∥ rep_id_numeric(2B) ∥ time_window(8B)
    msg = (
        org_id.to_bytes(1, "big") +
        rep_id_numeric.to_bytes(2, "big") +
        time_window.to_bytes(8, "big")
    )
    
    # Calculate HMAC
    digest = hmac.new(seed_bytes, msg, hashlib.sha256).digest()
    
    # Generate code
    code = int.from_bytes(digest, "big") % (10**digits)
    
    # Format code with leading zeros
    return f"{code:0{digits}d}"

