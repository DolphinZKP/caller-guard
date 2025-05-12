from utils.blockchain import blockchain_call
import time

def mint_new_agent(rep_id, bank_name):
    """Create a new agent record on the blockchain"""
    result = blockchain_call(
        "agent_manager.aleo",
        "mint_agent",
        [rep_id, bank_name]
    )
    
    # Generate a secure seed for OTP generation
    seed = generate_secure_seed()
    
    # Store the seed securely (off-chain)
    store_agent_seed(rep_id, bank_name, seed)
    
    return {
        "success": True,
        "agent_id": result["outputs"][0] if "outputs" in result else None,
        "rep_id": rep_id,
        "bank_name": bank_name
    }

def revoke_agent(agent_id, rep_id, bank_name):
    """Revoke an agent's access"""
    result = blockchain_call(
        "agent_manager.aleo",
        "revoke_agent",
        [agent_id]
    )
    
    # Update database to mark agent as revoked
    update_agent_status(rep_id, bank_name, "revoked")
    
    return {
        "success": True,
        "agent_id": agent_id,
        "status": "revoked"
    }

def check_agent_status(agent_id):
    """Check if an agent is active"""
    result = blockchain_call(
        "agent_manager.aleo",
        "is_agent_active",
        [agent_id]
    )
    
    return {
        "agent_id": agent_id,
        "is_active": result["outputs"][0] if "outputs" in result else False
    }

# Helper functions (would need implementation)
def generate_secure_seed():
    """Generate cryptographically secure random seed"""
    import os
    return int.from_bytes(os.urandom(8), 'big')

def store_agent_seed(rep_id, bank_name, seed):
    """Store seed securely in database"""
    # Implementation depends on your database setup
    pass

def update_agent_status(rep_id, bank_name, status):
    """Update agent status in database"""
    # Implementation depends on your database setup
    pass
