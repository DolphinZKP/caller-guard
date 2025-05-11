//1) Recompute the on-chain key:
let commit = poseidon_hash([bank_name, rep_id])

//2) Ensure badge exists & is active:
if not aleo_rpc.get_state("agents", key=commit):
    return {"verified": False}

//3) Recompute & check OTP off-chain…
