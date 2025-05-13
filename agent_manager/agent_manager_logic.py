import os
import sys
import json
import re

# Get the absolute path of the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the path to the project root directory (one level up from agent_manager)
project_root = os.path.join(script_dir, '..')

# Add the project root directory to sys.path
# This allows importing modules like 'utils' from the project root
sys.path.insert(0, project_root) # Use insert(0, ...) to prioritize project modules

# Now import the modules
from utils.blockchain import blockchain_call

def extract_record_from_output(output):
    """
    Extracts the first {...} block from Leo output.
    """
    match = re.search(r'\{[\s\S]*?\}', output)
    if match:
        return match.group(0)
    raise ValueError("No record found in Leo output")

def test_create_two_agents_with_blockchain_call():
    print("\n--- Test Case: Creating Two Agents Using blockchain_call ---")
    
    # First agent
    rep_id_1 = "1234field"  # Using proper Aleo field format
    bank_name_1 = "5678field"  # Using proper Aleo field format
    
    print("\nStep 1: Creating First Agent...")
    result_1 = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="mint_agent",
        inputs=[rep_id_1, bank_name_1],
        project_path="agent_manager"  # Specify the project path
    )
    
    assert result_1["success"], f"First agent creation failed: {result_1.get('error')}"
    print("First agent created successfully.")
    print(f"First agent result: {json.dumps(result_1, indent=2)}")
    
    # Second agent
    rep_id_2 = "9012field"  # Using proper Aleo field format
    bank_name_2 = "3456field"  # Using proper Aleo field format
    
    print("\nStep 2: Creating Second Agent...")
    result_2 = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="mint_agent",
        inputs=[rep_id_2, bank_name_2],
        project_path="agent_manager"  # Specify the project path
    )
    
    assert result_2["success"], f"Second agent creation failed: {result_2.get('error')}"
    print("Second agent created successfully.")
    print(f"Second agent result: {json.dumps(result_2, indent=2)}")
    
    print("\nResult: Both agents were successfully created.")
    print("Note: In a real blockchain environment, we would verify the records on-chain.")
    print("For testing purposes, we're relying on the success status of the blockchain calls.")

def test_create_duplicate_agents():
    print("\n--- Test Case: Attempting to Create Duplicate Agents ---")
    
    # Use the same identifiers for both agents
    rep_id = "1234field"
    bank_name = "5678field"
    
    print("\nStep 1: Creating First Agent...")
    result_1 = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="mint_agent",
        inputs=[rep_id, bank_name],
        project_path="agent_manager"
    )
    
    assert result_1["success"], f"First agent creation failed: {result_1.get('error')}"
    print("First agent created successfully.")
    print(f"First agent result: {json.dumps(result_1, indent=2)}")
    
    print("\nStep 2: Attempting to Create Duplicate Agent...")
    result_2 = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="mint_agent",
        inputs=[rep_id, bank_name],  # Same identifiers
        project_path="agent_manager"
    )
    
    print(f"Second attempt result: {json.dumps(result_2, indent=2)}")
    
    if result_2["success"]:
        print("\nWARNING: Successfully created duplicate agent! This might be a security issue.")
        print("The system should prevent creating multiple agents with the same identifiers.")
    else:
        print("\nSUCCESS: System correctly prevented creation of duplicate agent.")
        print("This is the expected behavior for security.")

def test_revoke_agent_twice():
    print("\n--- Test Case: Revoke Agent Twice ---")
    rep_id = "1234field"
    bank_name = "5678field"

    # 1. Create agent
    print("\nStep 1: Creating Agent...")
    create_result = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="mint_agent",
        inputs=[rep_id, bank_name],
        project_path="agent_manager"
    )
    assert create_result["success"], f"Agent creation failed: {create_result.get('error')}"
    print("Agent created successfully.")

    # After agent creation
    leo_output = create_result["raw_output"]
    print("DEBUG: Leo output:\n", leo_output)
    agent_record = extract_record_from_output(leo_output)

    # Then use agent_record as input:
    revoke_result = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="revoke_agent",
        inputs=[agent_record],
        project_path="agent_manager"
    )
    assert revoke_result["success"], f"First revocation failed: {revoke_result.get('error')}"
    print("Agent revoked successfully (first time).")

    # 3. Revoke agent (second time)
    print("\nStep 3: Revoking Agent (second time)...")
    revoke_result_2 = blockchain_call(
        program_name="agent_manager.aleo",
        function_name="revoke_agent",
        inputs=[agent_record],
        project_path="agent_manager"
    )
    print(f"Second revocation attempt result: {json.dumps(revoke_result_2, indent=2)}")
    if not revoke_result_2["success"]:
        print("SUCCESS: System correctly prevented double-spending (double revocation) of the agent record.")
    else:
        print("WARNING: System allowed double-spending, which should not happen!")

# Update the main block to include the new test
if __name__ == "__main__":
    #test_create_two_agents_with_blockchain_call()
    test_create_duplicate_agents()
    #test_revoke_agent_twice()
