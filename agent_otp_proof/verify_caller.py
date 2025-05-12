from utils.blockchain import blockchain_call
# In your verification backend
import time
def verify_caller(rep_id, bank_name, provided_otp):
    # 1. Get current timestamp
    current_time = int(time.time())
    seed = get_encrypted_seed(rep_id, bank_name) # get seed from HR secure storage
    
    # 2. Make GET requests from bank proof-registry-api
    # 2.a. Get the timestamp when OTP was generated from the client
    # Either client sends it or you retrieve from a recent OTP generation log
    generation_timestamp = get_otp_timestamp(rep_id, bank_name) 
    
    # 2.b Get agent status from blockchain
    agent = get_agent_record(rep_id, bank_name)
    status = agent.status
    
    # 2.c Calculate the expected OTP using seed from your secure storage
    expected_otp = generate_otp(rep_id, bank_name, generation_timestamp, seed)
    
    # 3. Call the verify_otp transition with all parameters including timestamps
    window_size = 60  # 60 seconds window
    result = blockchain_call(
        "agent_otp_proof_leo.aleo",
        "verify_otp",
        [rep_id, generation_timestamp, provided_otp, status, expected_otp, current_time, window_size]
    )
    
    return result