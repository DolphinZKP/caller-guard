"""Blockchain identity and related models."""

import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, 
    Integer, JSON, Text, Enum, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.db.base import Base
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class BlockchainIdentity(Base):
    """Blockchain identity for call center agents."""
    
    __tablename__ = "blockchain_identities"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True)
    employee = relationship("Employee", back_populates="blockchain_identity")
    
    # Aleo blockchain info
    aleo_address = Column(String(100), nullable=False, unique=True, index=True)
    private_key_encrypted = Column(String(500), nullable=False)
    view_key_encrypted = Column(String(500), nullable=False)
    
    # Agent identity details
    short_id = Column(Integer, nullable=False)
    seed = Column(String(500), nullable=False)  # Encrypted
    badge_ciphertext = Column(String(500), nullable=False)
    
    # OTP configuration
    otp_digits = Column(Integer, default=settings.DEFAULT_OTP_DIGITS, nullable=False)
    
    # Status flag
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert blockchain identity to dictionary.
        
        Args:
            include_secrets: Whether to include encrypted secrets in the output
            
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "aleo_address": self.aleo_address,
            "short_id": self.short_id,
            "otp_digits": self.otp_digits,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
        
        # Include secrets if requested (for admin purposes)
        if include_secrets:
            result.update({
                "private_key_encrypted": self.private_key_encrypted,
                "view_key_encrypted": self.view_key_encrypted,
                "seed": self.seed,
                "badge_ciphertext": self.badge_ciphertext
            })
            
        return result

class AuditLogAction(enum.Enum):
    """Enumeration of possible audit log actions."""
    
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # Employee actions
    EMPLOYEE_CREATE = "employee_create"
    EMPLOYEE_UPDATE = "employee_update"
    EMPLOYEE_DELETE = "employee_delete"
    
    # Agent actions
    AGENT_ENABLE = "agent_enable"
    AGENT_REVOKE = "agent_revoke"
    AGENT_OTP_GENERATE = "agent_otp_generate"
    
    # Admin actions
    SETTINGS_UPDATE = "settings_update"
    SYSTEM_MAINTENANCE = "system_maintenance"

class AuditLog(Base):
    """Audit logging for security and compliance."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Action details
    action = Column(Enum(AuditLogAction), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Actor information
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = Column(String(500), nullable=True)
    
    # Target information
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(String(50), nullable=True, index=True)
    
    # Additional data
    details = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="success", nullable=False)
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        return {
            "id": str(self.id),
            "action": self.action.value if self.action else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "status": self.status,
            "error_message": self.error_message
        }

class AuthAttemptResult(enum.Enum):
    """Enumeration of possible authentication attempt results."""
    
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    OTP_REQUIRED = "otp_required"
    OTP_INVALID = "otp_invalid"
    OTP_EXPIRED = "otp_expired"

class AuthAttempt(Base):
    """Authentication attempt tracking for security."""
    
    __tablename__ = "auth_attempts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Attempt details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    
    # Context
    user_agent = Column(String(500), nullable=True)
    result = Column(Enum(AuthAttemptResult), nullable=False)
    
    # Metadata
    details = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authentication attempt to dictionary."""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "username": self.username,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "result": self.result.value if self.result else None,
            "details": self.details
        }

