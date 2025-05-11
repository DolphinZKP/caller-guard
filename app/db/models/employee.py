"""Employee model and related functions."""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, 
    Integer, JSON, Text, text, Table, create_engine
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

class Employee(Base):
    """Employee model representing a call center employee."""
    
    __tablename__ = "employees"
    
    # Primary key and identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rep_id = Column(String(10), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Employment details
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # Permissions as JSON
    permissions = Column(JSON, nullable=False, default=lambda: settings.DEFAULT_PERMISSIONS)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    blockchain_identity = relationship("BlockchainIdentity", back_populates="employee", uselist=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee to dictionary."""
        return {
            "id": str(self.id),
            "rep_id": self.rep_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department": self.department,
            "position": self.position,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "has_blockchain_identity": self.blockchain_identity is not None
        }

def setup_rls_policies(engine) -> None:
    """Set up Row-Level Security (RLS) policies for PostgreSQL.
    
    This function creates RLS policies that control access to employee data
    based on the user's role and permissions.
    
    Args:
        engine: SQLAlchemy engine connected to PostgreSQL
    """
    # Skip if not PostgreSQL
    if settings.DB_TYPE.lower() != "postgresql":
        logger.warning("RLS policies can only be set up on PostgreSQL")
        return
    
    with engine.connect() as conn:
        # Enable RLS on the employees table
        conn.execute(text("ALTER TABLE employees ENABLE ROW LEVEL SECURITY"))
        
        # Create the policies for different roles
        
        # Admin policy - full access
        conn.execute(text("""
            CREATE POLICY admin_all_access ON employees 
            FOR ALL 
            TO admin_role 
            USING (true)
        """))
        
        # HR Manager policy - can view and modify all employees
        conn.execute(text("""
            CREATE POLICY hr_manager_access ON employees 
            FOR ALL 
            TO hr_manager_role 
            USING (true)
        """))
        
        # HR Staff policy - can view all employees but not modify
        conn.execute(text("""
            CREATE POLICY hr_staff_read_access ON employees 
            FOR SELECT 
            TO hr_staff_role 
            USING (true)
        """))
        
        # Agent policy - can only view own data
        conn.execute(text("""
            CREATE POLICY agent_own_access ON employees 
            FOR SELECT 
            TO agent_role 
            USING (username = current_setting('app.current_username'))
        """))
        
        logger.info("Successfully set up RLS policies for employee data")

