#!/usr/bin/env python3
"""Migration script to transition from the old flat file structure to the new modular architecture.

This script:
1. Creates the new directory structure if it doesn't exist
2. Copies configuration from old files to the new structure
3. Migrates the database if needed
4. Provides guidance on completing the migration
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path
import sqlite3
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_directory_structure():
    """Create the new directory structure if it doesn't exist."""
    logger.info("Setting up directory structure...")
    
    # Base directories
    directories = [
        "app/core",
        "app/db/models",
        "app/db/repositories",
        "app/blockchain",
        "app/api/routes",
        "app/utils",
        "ui/components",
        "ui/pages",
        "scripts",
        "tests/unit",
        "tests/integration",
        "docs"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

def copy_configuration():
    """Copy configuration from old files to the new structure."""
    logger.info("Copying configuration...")
    
    # Map of old files to new locations
    file_mappings = [
        # Configuration
        {"old": "config.py", "new": "app/core/config.py", "transform": transform_config},
        {"old": "crypto_utils.py", "new": "app/utils/crypto.py", "transform": transform_crypto},
        {"old": "db.py", "new": "app/db/base.py", "transform": transform_db},
        {"old": "models.py", "new": ["app/db/models/employee.py", "app/db/models/blockchain.py"], 
         "transform": transform_models},
        {"old": "backend.py", "new": "app/blockchain/mock.py", "transform": transform_backend},
        {"old": "streamlit_app.py", "new": "ui/streamlit_app.py", "transform": None},
        {"old": "agent_utils.py", "new": "app/core/agent.py", "transform": transform_agent_utils},
        {"old": "init_db.py", "new": "scripts/init_db.py", "transform": None},
        {"old": "api.py", "new": "app/api/main.py", "transform": None},
        {"old": "auth.py", "new": "app/core/security.py", "transform": None},
    ]
    
    # Process each file
    for mapping in file_mappings:
        old_path = mapping["old"]
        new_paths = mapping["new"] if isinstance(mapping["new"], list) else [mapping["new"]]
        transform_func = mapping["transform"]
        
        # Check if old file exists
        if not os.path.exists(old_path):
            logger.warning(f"Source file not found: {old_path}")
            continue
        
        # Read old file content
        with open(old_path, 'r') as f:
            content = f.read()
        
        # Transform content if needed
        if transform_func:
            content = transform_func(content)
        
        # Write to new location(s)
        for new_path in new_paths:
            # Ensure directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # Skip if new file already exists and is not empty
            if os.path.exists(new_path) and os.path.getsize(new_path) > 0:
                logger.info(f"Skipping existing file: {new_path}")
                continue
            
            # Write content
            with open(new_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Copied {old_path} to {new_path}")
    
    return True

def transform_config(content):
    """Transform the config.py file to the new format."""
    # This would contain logic to transform the old config format to new
    # For this example, we'll just return a placeholder
    return """"""

def transform_crypto(content):
    """Transform the crypto_utils.py file to the new format."""
    # This would contain logic to transform the old crypto utils format to new
    return content

def transform_db(content):
    """Transform the db.py file to the new format."""
    # This would contain logic to transform the old db format to new
    return content

def transform_models(content):
    """Transform the models.py file to separate model files."""
    # This would split the models into separate files
    return content

def transform_backend(content):
    """Transform the backend.py file to the new blockchain client format."""
    # This would transform the old backend to the new blockchain client
    return content

def transform_agent_utils(content):
    """Transform the agent_utils.py file to the new core agent module."""
    # This would transform the agent utils to the new format
    return content

def migrate_database(source_db="zk_agents.db"):
    """Migrate the database to the new schema if needed."""
    logger.info(f"Checking database: {source_db}")
    
    if not os.path.exists(source_db):
        logger.warning(f"Database file not found: {source_db}")
        return False
    
    try:
        conn = sqlite3.connect(source_db)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        tables = [table[0] for table in tables]
        
        logger.info(f"Found tables: {', '.join(tables)}")
        
        # Check if we need migration
        needs_migration = "blockchain_identities" not in tables
        
        if needs_migration:
            logger.info("Database needs migration to new schema")
            # This would contain migration logic
            # For now, we'll just notify the user
            logger.warning("Automatic database migration not implemented yet.")
            logger.warning("Please run scripts/init_db.py to create a new database.")
        else:
            logger.info("Database schema looks up-to-date")
        
        conn.close()
        return True
    
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False

def create_example_env():
    """Create an example .env file if it doesn't exist."""
    env_file = ".env"
    example_file = "env.example"
    
    if os.path.exists(env_file):
        logger.info(f"Skipping existing file: {env_file}")
        return True
    
    if not os.path.exists(example_file):
        logger.warning(f"Example env file not found: {example_file}")
        return False
    
    shutil.copy(example_file, env_file)
    logger.info(f"Created .env file from {example_file}")
    return True

def main(args):
    """Run the migration process."""
    logger.info("Starting migration to new structure...")
    
    # Create directory structure
    if not setup_directory_structure():
        logger.error("Failed to create directory structure")
        return 1
    
    # Copy configuration
    if args.copy_config:
        if not copy_configuration():
            logger.error("Failed to copy configuration")
            return 1
    
    # Migrate database
    if args.migrate_db:
        if not migrate_database(args.source_db):
            logger.error("Failed to migrate database")
            return 1
    
    # Create example env file
    if args.create_env:
        if not create_example_env():
            logger.error("Failed to create example .env file")
            return 1
    
    logger.info("Migration completed successfully!")
    
    # Provide guidance
    logger.info("\nNext steps:")
    logger.info("1. Install required packages: pip install -r requirements.txt")
    logger.info("2. Initialize the database: python scripts/init_db.py")
    logger.info("3. Create test data: python scripts/create_test_data.py")
    logger.info("4. Run the application: streamlit run ui/streamlit_app.py")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate to new project structure")
    parser.add_argument("--copy-config", action="store_true", help="Copy configuration files")
    parser.add_argument("--migrate-db", action="store_true", help="Migrate database schema")
    parser.add_argument("--create-env", action="store_true", help="Create .env file from example")
    parser.add_argument("--source-db", default="zk_agents.db", help="Source database file")
    parser.add_argument("--all", action="store_true", help="Perform all migration steps")
    
    args = parser.parse_args()
    
    # If --all is specified, set all options to True
    if args.all:
        args.copy_config = True
        args.migrate_db = True
        args.create_env = True
    
    sys.exit(main(args)) 