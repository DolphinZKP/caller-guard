"""__init__.py"""

from app.blockchain.mock import get_blockchain_client

# Import and export the global client factory
__all__ = ["get_blockchain_client"]

