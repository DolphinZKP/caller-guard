import os
import sys
import subprocess
import json

# Add the project root to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
sys.path.insert(0, project_root)

from utils.blockchain import blockchain_call
import time
import sqlite3

# Setup DB (could be in-memory for tests)
conn = sqlite3.connect(':memory:')
db = conn.cursor()
db.execute('CREATE TABLE otp_sessions (rep_id TEXT, bank_name TEXT, timestamp INTEGER, expires_at INTEGER)')
conn.commit()

def to_field(val):
    val = str(val)
    return val if val.endswith("field") else f"{val}field"

def to_u64(val):
    val = str(val)
    return val if val.endswith("u64") else f"{val}u64"

# When generating OTP
def generate_agent_otp(rep_id: str, bank_name: str, seed: int, db: sqlite3.Connection):
    generation_timestamp = int(time.time())
    rep_id = to_field(rep_id)
    bank_name = to_field(bank_name)
    seed = to_field(seed)
    #timestamp_str = f'"{generation_timestamp}"'  # Just quote it, don't add "field"
    otp = blockchain_call(
        "agent_otp_generate.aleo",
        "generate_otp",
        [rep_id, bank_name, to_u64(generation_timestamp), seed]
    )
    db.execute(
        "INSERT INTO otp_sessions (rep_id, bank_name, timestamp, expires_at) VALUES (?, ?, ?, ?)",
        [rep_id, bank_name, generation_timestamp, generation_timestamp + 60]
    )
    conn.commit()  # Explicitly commit the transaction
    
    # Verify the write
    db.execute("SELECT * FROM otp_sessions WHERE rep_id = ? AND timestamp = ?", [rep_id, generation_timestamp])
    result = db.fetchone()
    if not result:
        raise Exception("Failed to verify database write")
        
    return {"otp": otp, "timestamp": generation_timestamp}

def generate_zk_proof(rep_id, bank_name, seed, timestamp, otp, proof_json_path=None):
    """
    Generates a ZK proof using snarkvm execute and saves the output JSON to a file in the output folder.
    Returns the parsed JSON object.
    """
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    if proof_json_path is None:
        proof_json_path = os.path.join(output_dir, "proof.json")

    # Prepare the command
    cmd = [
        "snarkvm", "execute", "prove_otp_generation",
        rep_id, bank_name, seed, f"{timestamp}u64", f"{otp}u32"
    ]
    # Run the command and capture output
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    # Find the JSON in the output (snarkvm prints it after the result)
    json_start = output.find('{')
    json_end = output.rfind('}') + 1
    if json_start == -1 or json_end == -1:
        raise Exception("Could not find JSON output in snarkvm response.")

    proof_json = output[json_start:json_end]
    proof_data = json.loads(proof_json)

    # Save to file
    with open(proof_json_path, "w") as f:
        f.write(proof_json)

    print(f"Proof JSON saved to {proof_json_path}")
    return proof_data

if __name__ == "__main__":
    # Call the function
    result = generate_agent_otp("1233", "5678", 123, db)    
    print(f"Generated OTP: {result['otp']}")
    print(f"Timestamp: {result['timestamp']}")

    # Verify the database write using the actual values
    db.execute("SELECT * FROM otp_sessions")
    all_records = db.fetchall()
    print("\nAll records in database:")
    for record in all_records:
        print(f"Record: {record}")
    
    # Verify with the actual values used in the write
    db.execute("SELECT * FROM otp_sessions WHERE rep_id = ? AND timestamp = ?", 
              [to_field("1233"), result['timestamp']])
    verify_result = db.fetchone()
    if not verify_result:
        raise Exception("Failed to verify database write")
    print(f"\nDatabase write verified: {verify_result}")

    # Example usage of generate_zk_proof
    # placeholder variables
    rep_id = "1233field"
    bank_name = "5678field"
    seed = "123field"
    timestamp = "1747100401"
    otp = "100401"
    proof = generate_zk_proof(rep_id, bank_name, seed, timestamp, otp)
    print(json.dumps(proof, indent=2))