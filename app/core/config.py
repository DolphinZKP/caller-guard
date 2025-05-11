"""config.py"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

class Settings:
    """Application settings loaded from environment variables with defaults."""
    
    # Project information
    PROJECT_NAME: str = "ZK Caller Verification"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A zero-knowledge proof system for call center agent verification"
    
    # Environment settings
    DEBUG: bool = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.environ.get("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Database configuration
    DB_TYPE: str = os.environ.get("DB_TYPE", "sqlite")
    DB_HOST: str = os.environ.get("DB_HOST", "localhost")
    DB_PORT: str = os.environ.get("DB_PORT", "5432")
    DB_USER: str = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
    DB_NAME: str = os.environ.get("DB_NAME", "zk_agents")
    DB_PATH: str = os.environ.get("DB_PATH", "zk_agents.db")
    
    # Computed database URL
    @property
    def DATABASE_URL(self) -> str:
        """Assemble database URL from components."""
        if self.DB_TYPE.lower() == "postgresql":
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"sqlite:///{self.DB_PATH}"
    
    # Security settings
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.environ.get("JWT_EXPIRATION_MINUTES", "30"))
    
    ADMIN_USERNAME: str = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "")
    
    # Crypto settings
    FERNET_KEY: str = os.environ.get("FERNET_KEY", "")
    
    # Blockchain settings
    TRUSTED_PROGRAM_ID: str = os.environ.get("TRUSTED_PROGRAM_ID", "zk_verify.aleo")
    CALLCENTRE_ADMIN_PK: str = os.environ.get("CALLCENTRE_ADMIN_PK", "")
    ORG_ID: int = int(os.environ.get("ORG_ID", "171"))
    
    # OTP settings
    DEFAULT_OTP_DIGITS: int = int(os.environ.get("DEFAULT_OTP_DIGITS", "6"))
    OTP_WINDOW_SIZE: int = 60  # Force exactly 60 seconds (1 minute)
    
    # Default permissions for new agents
    DEFAULT_PERMISSIONS: Dict[str, bool] = {
        'can_open_acc': True,
        'can_take_pay': False
    }
    
    # User roles
    USER_ROLES: Dict[str, List[str]] = {
        'admin': ['read_all', 'write_all'],
        'hr_manager': ['read_employees', 'write_employees', 'enable_agents', 'revoke_agents'],
        'hr_staff': ['read_employees'],
        'agent': ['read_self', 'generate_code']
    }
    
    def get_crypto_key(self) -> bytes:
        """Get or generate Fernet key for encryption."""
        if not self.FERNET_KEY:
            from cryptography.fernet import Fernet
            print("FERNET_KEY not found in environment, generating one for development...")
            key = Fernet.generate_key().decode()
            print(f"Generated key: {key} - In production, set this in environment")
            return key.encode()
        return self.FERNET_KEY.encode()
    
    def validate(self) -> None:
        """Validate configuration to ensure it meets requirements."""
        if self.ENVIRONMENT == "production":
            assert self.DB_TYPE == "postgresql", "Production environment requires PostgreSQL database"
            assert len(self.JWT_SECRET_KEY) >= 32, "Production environment requires strong JWT secret key"
            assert self.FERNET_KEY, "Production environment requires FERNET_KEY to be set"
            assert self.ADMIN_PASSWORD, "Production environment requires ADMIN_PASSWORD to be set"

# Create global settings instance
settings = Settings()

# Auto-validate in production
if settings.ENVIRONMENT == "production":
    settings.validate()

