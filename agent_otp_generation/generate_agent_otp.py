import os
import sys
import subprocess

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
    return {"otp": otp, "timestamp": generation_timestamp}


if __name__ == "__main__":
    # Call the function
    result = generate_agent_otp("1233", "5678", 123, db)    
    print(f"Generated OTP: {result['otp']}")
    print(f"Timestamp: {result['timestamp']}")
