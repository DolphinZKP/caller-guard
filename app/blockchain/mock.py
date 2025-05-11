"""mock.py"""

import random
import uuid
import hmac
import hashlib
import time
import logging
from typing import Dict, Any, Tuple, Optional

from app.blockchain.client import BlockchainClient
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class MockBlockchainClient(BlockchainClient):
    """Mock implementation of the blockchain client for testing and development."""
    
    def create_account(self) -> Tuple[str, str, str]:
        """Create a mock blockchain account.
        
        Returns:
            Tuple[str, str, str]: (address, private_key, view_key)
        """
        addr = f"aleo1{random.randint(10**20, 10**30)}"
        priv = f"APrivateKey1{random.randint(10**30, 10**40)}"
        view = f"AViewKey1{random.randint(10**30, 10**40)}"
        
        logger.info(f"[DEMO] Generated mock Aleo account: {addr}")
        return addr, priv, view
    
    def mint_badge(self, 
                  first_name: str, 
                  last_name: str, 
                  username: str, 
                  rep_id: str,
                  org_id: int, 
                  short_id: int,
                  seed: int,
                  digits: int,
                  permissions: Dict[str, bool]) -> Dict[str, Any]:
        """Mint a mock badge for an agent.
        
        Args:
            first_name: Agent's first name
            last_name: Agent's last name
            username: Agent's username
            rep_id: Agent's representative ID
            org_id: Organization ID
            short_id: Numeric short ID
            seed: Seed for OTP generation
            digits: Number of digits in OTP
            permissions: Map of permission names to boolean values
            
        Returns:
            Dict[str, Any]: Complete agent information including blockchain identity
        """
        # Generate new Aleo account
        aleo_addr, priv_key, view_key = self.create_account()
        
        # Generate a unique user key
        user_key = str(uuid.uuid4())
        
        # Simulate minting in demo mode
        badge_cipher = f"demo_badge_{rep_id}_{uuid.uuid4().hex}"
        logger.info(f"[DEMO] Simulated minting badge for agent: {rep_id}")
        
        # Return complete agent info
        return {
            "id": uuid.uuid4().hex,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "rep_id": rep_id,
            "aleo_address": aleo_addr,
            "private_key": priv_key,
            "view_key": view_key,
            "user_key": user_key,
            "seed": seed,
            "short_id": short_id,
            "otp_digits": digits,
            "permissions": permissions,
            "org_id": org_id,
            "badge_ciphertext": badge_cipher
        }
    
    def revoke_badge(self, badge_id: str) -> Dict[str, Any]:
        """Revoke a mock agent badge.
        
        Args:
            badge_id: The badge identifier to revoke
            
        Returns:
            Dict[str, Any]: Result of the revocation operation
        """
        logger.info(f"[DEMO] Simulated revoking badge: {badge_id}")
        return {
            "status": "success", 
            "message": "Agent badge revoked successfully in demo mode"
        }
    
    def generate_otp(self, 
                    seed: int, 
                    org_id: int, 
                    rep_id_numeric: int,
                    time_window: int, 
                    digits: int = 6) -> Tuple[str, int]:
        """Generate a one-time password for agent verification.
        
        In the mock implementation, we still use a proper HMAC-based implementation
        to ensure the OTP codes change regularly and are deterministic.
        
        Args:
            seed: Secret seed value
            org_id: Organization ID
            rep_id_numeric: Numeric representation of agent ID
            time_window: Current time window
            digits: Number of digits in the OTP
            
        Returns:
            Tuple[str, int]: (otp_code, time_window)
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
        return f"{code:0{digits}d}", time_window

# Factory function to create client
def get_blockchain_client() -> BlockchainClient:
    """Create and return a blockchain client instance.
    
    In production, this would create the real Aleo implementation.
    In development/test mode, it creates the mock implementation.
    
    Returns:
        BlockchainClient: The appropriate blockchain client implementation
    """
    if settings.DEMO_MODE:
        logger.info("Using mock blockchain client")
        return MockBlockchainClient()
    else:
        # In the future, we'd import and return the real implementation
        # from app.blockchain.aleo import AleoBlockchainClient
        # return AleoBlockchainClient()
        
        # For now, always return the mock implementation
        logger.warning("Real blockchain client not implemented, using mock")
        return MockBlockchainClient()

