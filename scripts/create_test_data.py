#!/usr/bin/env python3
"""Create test data for development and testing.

This script creates:
- Sample HR users with different roles
- Sample employees
- Some enabled agents with blockchain identities
"""

import os
import sys
import argparse
import logging
import uuid
import random
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import Base, engine, SessionLocal
from app.db.models.user import User, UserRole
from app.db.models.employee import Employee
from app.db.models.blockchain import BlockchainIdentity, AuditLog, AuditLogAction
from app.core.config import settings
from app.blockchain import get_blockchain_client
from app.utils.crypto import encrypt, generate_numeric_hash

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample departments and positions
DEPARTMENTS = ["Sales", "Customer Support", "Technical Support", "Billing", "Claims"]
POSITIONS = {
    "Sales": ["Sales Agent", "Senior Sales Agent", "Sales Team Lead"],
    "Customer Support": ["Customer Service Representative", "Senior Customer Service Agent", "Support Team Lead"],
    "Technical Support": ["Technical Support Agent", "Senior Technical Specialist", "Tech Lead"],
    "Billing": ["Billing Agent", "Billing Specialist", "Billing Manager"],
    "Claims": ["Claims Agent", "Claims Processor", "Claims Supervisor"]
}

# Sample names
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez",
    "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans",
    "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook"
]

def generate_password_hash(password: str) -> str:
    """Generate a password hash for testing.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    import hashlib
    salt = os.urandom(16).hex()
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt
    return hashed_password

def create_hr_users(db: SessionLocal) -> List[User]:
    """Create sample HR users with different roles.
    
    Args:
        db: Database session
        
    Returns:
        List[User]: Created users
    """
    logger.info("Creating sample HR users...")
    
    users = []
    
    # Create one user of each role
    roles_data = [
        {
            "username": "admin",
            "password": "admin123",  # Change in production!
            "full_name": "System Administrator",
            "role": UserRole.ADMIN,
            "is_superuser": True
        },
        {
            "username": "hr_manager",
            "password": "manager123",  # Change in production!
            "full_name": "Jane Manager",
            "role": UserRole.HR_MANAGER,
            "is_superuser": False
        },
        {
            "username": "hr_staff",
            "password": "staff123",  # Change in production!
            "full_name": "Bob Staff",
            "role": UserRole.HR_STAFF,
            "is_superuser": False
        }
    ]
    
    for user_data in roles_data:
        # Check if user already exists
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            logger.info(f"User '{user_data['username']}' already exists")
            users.append(existing)
            continue
        
        user = User(
            username=user_data["username"],
            hashed_password=generate_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True,
            is_superuser=user_data["is_superuser"]
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created user: {user.username} ({user.role.value})")
        users.append(user)
        
        # Log the action
        log_entry = AuditLog(
            action=AuditLogAction.USER_CREATE,
            user_id=user.id,
            resource_type="user",
            resource_id=str(user.id),
            details={"username": user.username, "role": user.role.value}
        )
        db.add(log_entry)
        db.commit()
    
    return users

def create_employee(db: SessionLocal) -> Employee:
    """Create a sample employee with random data.
    
    Args:
        db: Database session
        
    Returns:
        Employee: Created employee
    """
    # Generate random employee data
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    department = random.choice(DEPARTMENTS)
    position = random.choice(POSITIONS[department])
    
    # Generate username from initials and numbers
    username = f"{first_name[0]}{last_name[0]}{random.randint(100, 999)}"
    
    # Generate rep_id (format: letter + numbers)
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # Omitting I and O to avoid confusion
    rep_id = f"{random.choice(letters)}{random.randint(1000, 9999)}"
    
    # Generate random permissions
    permissions = {
        'can_open_acc': random.choice([True, False]),
        'can_take_pay': random.choice([True, False])
    }
    
    # Create the employee
    employee = Employee(
        first_name=first_name,
        last_name=last_name,
        username=username,
        rep_id=rep_id,
        department=department,
        position=position,
        permissions=permissions
    )
    
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    logger.info(f"Created employee: {employee.first_name} {employee.last_name} ({employee.rep_id})")
    
    return employee

def enable_agent(db: SessionLocal, employee: Employee) -> BlockchainIdentity:
    """Enable an employee as an agent with blockchain identity.
    
    Args:
        db: Database session
        employee: Employee to enable
        
    Returns:
        BlockchainIdentity: Created blockchain identity
    """
    # Check if already enabled
    if employee.blockchain_identity:
        logger.info(f"Agent {employee.rep_id} already enabled")
        return employee.blockchain_identity
    
    logger.info(f"Enabling agent: {employee.first_name} {employee.last_name} ({employee.rep_id})")
    
    # Get blockchain client
    blockchain = get_blockchain_client()
    
    # Generate seed for OTP
    seed = random.randint(10**6, 10**8)
    
    # Generate short ID from rep_id
    short_id = generate_numeric_hash(employee.rep_id, 2)
    
    # Create blockchain badge
    result = blockchain.mint_badge(
        first_name=employee.first_name,
        last_name=employee.last_name,
        username=employee.username,
        rep_id=employee.rep_id,
        org_id=settings.ORG_ID,
        short_id=short_id,
        seed=seed,
        digits=settings.DEFAULT_OTP_DIGITS,
        permissions=employee.permissions
    )
    
    # Create blockchain identity
    identity = BlockchainIdentity(
        employee_id=employee.id,
        aleo_address=result["aleo_address"],
        private_key_encrypted=encrypt(result["private_key"]),
        view_key_encrypted=encrypt(result["view_key"]),
        short_id=short_id,
        seed=encrypt(seed),
        badge_ciphertext=result["badge_ciphertext"],
        otp_digits=settings.DEFAULT_OTP_DIGITS,
        is_active=True
    )
    
    db.add(identity)
    db.commit()
    db.refresh(identity)
    
    logger.info(f"Successfully enabled agent: {employee.rep_id}")
    
    # Log the action
    log_entry = AuditLog(
        action=AuditLogAction.AGENT_ENABLE,
        resource_type="employee",
        resource_id=str(employee.id),
        user_id=None,
        details={
            "rep_id": employee.rep_id,
            "aleo_address": result["aleo_address"]
        }
    )
    db.add(log_entry)
    db.commit()
    
    return identity

def main(args):
    """Create test data for development and testing.
    
    Args:
        args: Command line arguments
    """
    db = SessionLocal()
    try:
        # Create sample HR users
        create_hr_users(db)
        
        # Create sample employees
        count = args.count
        logger.info(f"Creating {count} sample employees...")
        
        employees = []
        for i in range(count):
            employee = create_employee(db)
            employees.append(employee)
        
        # Force zero enabled agents, ignoring command line argument
        args.enable = 0
        logger.info("No agents will be pre-enabled. Use HR Admin to enable agents.")
        
        # Enable some employees as agents
        if args.enable:
            logger.info(f"Enabling {args.enable} employees as agents...")
            
            enabled_count = min(args.enable, len(employees))
            for i in range(enabled_count):
                enable_agent(db, employees[i])
        
        logger.info("Test data creation completed successfully!")
        return 0
    
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        return 1
    
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create test data for development and testing")
    parser.add_argument("--count", type=int, default=10, help="Number of employees to create")
    parser.add_argument("--enable", type=int, default=3, help="Number of employees to enable as agents")
    
    args = parser.parse_args()
    
    sys.exit(main(args))

