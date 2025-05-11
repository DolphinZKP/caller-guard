"""client.py"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional

class BlockchainClient(ABC):
    """Abstract base class for blockchain operations.
    
    This allows us to have different implementations:
    - Real Aleo implementation for production
    - Mock implementation for testing and development
    """
    
    @abstractmethod
    def create_account(self) -> Tuple[str, str, str]:
        """Create a new blockchain account.
        
        Returns:
            Tuple[str, str, str]: (address, private_key, view_key)
        """
        pass
    
    @abstractmethod
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
        """Mint a badge for an agent.
        
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
        pass
    
    @abstractmethod
    def revoke_badge(self, badge_id: str) -> Dict[str, Any]:
        """Revoke an agent badge.
        
        Args:
            badge_id: The badge identifier to revoke
            
        Returns:
            Dict[str, Any]: Result of the revocation operation
        """
        pass
    
    @abstractmethod
    def generate_otp(self, 
                    seed: int, 
                    org_id: int, 
                    rep_id_numeric: int,
                    time_window: int, 
                    digits: int = 6) -> Tuple[str, int]:
        """Generate a one-time password for agent verification.
        
        Args:
            seed: Secret seed value
            org_id: Organization ID
            rep_id_numeric: Numeric representation of agent ID
            time_window: Current time window
            digits: Number of digits in the OTP
            
        Returns:
            Tuple[str, int]: (otp_code, time_window)
        """
        pass

