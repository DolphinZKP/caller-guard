#!/usr/bin/env python3
"""
Main entry point for ZK Caller Verification System.
This script:
1. Initializes the database if not set up
2. Creates test data if needed
3. Launches the Streamlit UI
"""

import os
import sys
import logging
import argparse
import subprocess
import getpass
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database():
    """Check if database is initialized by verifying if tables exist."""
    try:
        # Import needed modules
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from app.db.base import engine
        from sqlalchemy import inspect
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # If we have tables, database is initialized
        if len(tables) > 0:
            logger.info(f"Database exists with {len(tables)} tables")
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return False

def init_database(username=None, password=None, interactive=True):
    """Initialize the database tables and admin user.
    
    Args:
        username: Admin username
        password: Admin password
        interactive: Whether to prompt for credentials if not provided
        
    Returns:
        bool: Whether initialization was successful
    """
    logger.info("Initializing database...")
    
    cmd = [sys.executable, "scripts/init_db.py"]
    
    # Add username if provided
    if username:
        cmd.extend(["--username", username])
        
    # Add password if provided
    if password:
        cmd.extend(["--password", password])
    
    try:
        if interactive and not (username and password):
            # Run interactively if credentials not provided
            logger.info("Running database initialization interactively...")
            result = subprocess.run(cmd)
            return result.returncode == 0
        else:
            # Run non-interactively with provided credentials
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Database initialization completed.")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Database initialization failed: {e.stderr}")
        return False

def create_test_data(count=10, enable=0):
    """Create test data for the application."""
    logger.info(f"Creating test data: {count} employees, {enable} enabled agents...")
    try:
        # Run the create_test_data.py script
        result = subprocess.run(
            [sys.executable, "scripts/create_test_data.py", "--count", str(count), "--enable", str(enable)],
            capture_output=True, 
            text=True,
            check=True
        )
        logger.info("Test data creation completed.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Test data creation failed: {e.stderr}")
        return False

def launch_streamlit():
    """Launch the Streamlit UI."""
    logger.info("Launching Streamlit UI...")
    
    # Launch Streamlit
    try:
        # We're not capturing output here so the user can see Streamlit's output
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "ui/streamlit_app.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return process
    except Exception as e:
        logger.error(f"Error launching Streamlit: {e}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ZK Caller Verification System")
    parser.add_argument("--skip-init", action="store_true", help="Skip database initialization")
    parser.add_argument("--skip-test-data", action="store_true", help="Skip test data creation")
    parser.add_argument("--employees", type=int, default=10, help="Number of test employees to create")
    parser.add_argument("--agents", type=int, default=5, help="Number of test agents to enable")
    parser.add_argument("--username", help="Admin username for database initialization")
    parser.add_argument("--password", help="Admin password for database initialization")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    
    args = parser.parse_args()
    
    # Check if database is initialized
    db_initialized = check_database()
    
    # Initialize database if needed
    if not db_initialized and not args.skip_init:
        # If running non-interactively, ensure credentials are provided
        if args.non_interactive and not (args.username and args.password):
            logger.error("In non-interactive mode, both --username and --password must be provided")
            return 1
            
        # Get admin credentials if not provided and in interactive mode
        username = args.username
        password = args.password
        
        if not args.non_interactive and not username:
            username = input("Admin username [admin]: ") or "admin"
            
        if not args.non_interactive and not password:
            password = getpass.getpass("Admin password: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                logger.error("Passwords don't match")
                return 1
        
        # Initialize the database
        if not init_database(username, password, not args.non_interactive):
            logger.error("Failed to initialize database. Exiting.")
            return 1
    
    # Create test data if requested
    if not args.skip_test_data:
        if not create_test_data(args.employees, args.agents):
            logger.warning("Failed to create test data, but continuing with app launch.")
    
    # Launch Streamlit UI
    process = launch_streamlit()
    if not process:
        logger.error("Failed to launch Streamlit UI. Exiting.")
        return 1
    
    # Wait for the Streamlit process to finish
    try:
        process.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        process.terminate()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 