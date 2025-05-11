"""Base database configuration."""

import logging
from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine for SQLite
engine = create_engine(settings.DATABASE_URL)

# Enable foreign key constraints in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Import models here to avoid circular imports
    from app.db.models.user import User
    from app.db.models.employee import Employee
    from app.db.models.blockchain import BlockchainIdentity, AuditLog, AuthAttempt
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

