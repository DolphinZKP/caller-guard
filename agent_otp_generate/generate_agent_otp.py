from utils.blockchain import blockchain_call
import time

# When generating OTP
def generate_agent_otp(rep_id, bank_name):
    # 1. Get current timestamp
    generation_timestamp = int(time.time())
    
    # 2. Get seed from secure storage
    seed = get_secure_seed(rep_id, bank_name)
    
    # 3. Generate OTP
    otp = blockchain_call(
        "agent_otp_generate.aleo",
        "generate_otp",
        [rep_id, bank_name, generation_timestamp, seed]
    )
    
    # 4. Store timestamp temporarily
    db.execute(
        "INSERT INTO otp_sessions (rep_id, bank_name, timestamp, expires_at) VALUES (?, ?, ?, ?)",
        [rep_id, bank_name, generation_timestamp, generation_timestamp + 60]
    )
    
    return {"otp": otp, "timestamp": generation_timestamp}