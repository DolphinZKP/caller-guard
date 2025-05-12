# test_blockchain_call.py
import os
import sys
import json

# Add path to utils directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the blockchain_call function
from utils.blockchain import blockchain_call

def test_local_execution():
    """Test locally executing a function"""
    print("Testing local execution:")
    result = blockchain_call(
        "agent_manager.aleo", 
        "mint_agent",
        ["1234field", "5678field"],
        project_path="/mnt/d/caller-guard/agent_manager"
    )
    print(f"Result: {json.dumps(result, indent=2)}")

def test_deployed_execution():
    """Test executing on the deployed program"""
    print("Testing deployed execution:")
    # Add the --network and --endpoint flags for deployed tests
    result = blockchain_call(
        "agent_manager.aleo", 
        "mint_agent",
        ["1234field", "5678field"],
        project_path="/mnt/d/caller-guard/agent_manager",
        is_deployed=True,
        network="testnet",
        endpoint="https://api.explorer.aleo.org/v1"
    )
    print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    # Test local first
    test_local_execution()
    
    # Test deployed version
    test_deployed_execution()