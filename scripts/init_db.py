#!/usr/bin/env python3
"""Database initialization script.

This script creates all tables and sets up initial data:
- Admin user
- Default roles and permissions
- PostgreSQL RLS policies (if applicable)
"""

import os
import sys
import argparse
import logging
import uuid
import getpass
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import Base, engine, init_db
from app.db.models.user import User, UserRole
from app.db.models.employee import Employee
from app.db.models.blockchain import BlockchainIdentity, AuditLog, AuditLogAction, AuthAttempt
from app.core.config import settings
from app.utils.crypto import get_fernet
from sqlalchemy.orm import Session, sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin_user(db: Session, username: str, password: str) -> User:
    """Create an admin user.
    
    Args:
        db: Database session
        username: Admin username
        password: Admin password
        
    Returns:
        User: Created admin user
    """
    import hashlib
    # Check if admin already exists
    admin = db.query(User).filter(User.username == username).first()
    if admin:
        logger.info(f"Admin user '{username}' already exists")
        return admin
    
    # Hash the password (in a real app, use a proper password hashing lib like bcrypt or Argon2)
    salt = os.urandom(16).hex()
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt
    
    # Create admin user
    admin = User(
        username=username,
        hashed_password=hashed_password,
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    logger.info(f"Created admin user '{username}'")
    
    # Log the action
    log_entry = AuditLog(
        action=AuditLogAction.USER_CREATE,
        user_id=admin.id,
        resource_type="user",
        resource_id=str(admin.id),
        details={"username": username, "role": UserRole.ADMIN.value, "is_superuser": True}
    )
    db.add(log_entry)
    db.commit()
    
    return admin

def main(args):
    """Initialize the database.
    
    Args:
        args: Command line arguments
    """
    # Create tables
    logger.info("Creating database tables...")
    init_db()
    
    # Get or create admin credentials
    admin_username = args.username or settings.ADMIN_USERNAME or input("Admin username: ")
    
    if args.password:
        admin_password = args.password
    elif settings.ADMIN_PASSWORD:
        admin_password = settings.ADMIN_PASSWORD
    else:
        admin_password = getpass.getpass("Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        if admin_password != confirm_password:
            logger.error("Passwords do not match!")
            return 1
    
    # Create a database session
    db = SessionLocal()
    try:
        # Create admin user
        admin = create_admin_user(db, admin_username, admin_password)
        
        # Log initialization
        log_entry = AuditLog(
            action=AuditLogAction.SYSTEM_MAINTENANCE,
            user_id=admin.id,
            details={"operation": "database_initialization", "timestamp": datetime.utcnow().isoformat()}
        )
        db.add(log_entry)
        db.commit()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--username", help="Admin username")
    parser.add_argument("--password", help="Admin password")
    parser.add_argument("--force", action="store_true", help="Force recreation of tables")
    
    args = parser.parse_args()
    
    sys.exit(main(args))

