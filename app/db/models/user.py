"""User model for authentication and authorization."""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class UserRole(enum.Enum):
    """User roles that determine permissions."""
    
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    HR_STAFF = "hr_staff"
    AGENT = "agent"

class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    hashed_password = Column(String(100), nullable=False)
    
    # Profile information
    full_name = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.HR_STAFF)
    permissions = Column(JSON, nullable=True)  # Optional custom permissions
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    password_reset_token = Column(String(100), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Employee link - optional, for agent users that correspond to an employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def to_dict(self, include_security: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary.
        
        Args:
            include_security: Whether to include security-related fields
            
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "employee_id": str(self.employee_id) if self.employee_id else None
        }
        
        # Include security info if requested (for admin purposes)
        if include_security:
            result.update({
                "failed_login_attempts": self.failed_login_attempts,
                "has_password_reset": self.password_reset_token is not None,
                "password_reset_expires": self.password_reset_expires.isoformat() if self.password_reset_expires else None
            })
            
        return result
    
    def get_permissions(self) -> List[str]:
        """Get the list of permissions for this user.
        
        Returns:
            List[str]: List of permission strings
        """
        # Start with role-based permissions
        permissions = settings.USER_ROLES.get(self.role.value, []) if self.role else []
        
        # Add custom permissions
        if self.permissions:
            for perm, enabled in self.permissions.items():
                if enabled and perm not in permissions:
                    permissions.append(perm)
        
        # Superusers have all permissions
        if self.is_superuser:
            permissions = list(set(permissions + ['read_all', 'write_all']))
            
        return permissions

