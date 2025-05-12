program agent_otp_proof.aleo {
    // Main verification function with time window validation
    transition verify_otp(
        agent_id: field,         
        timestamp: u64,          // When OTP was generated
        provided_otp: u32,       
        agent_status: u8,        
        expected_otp: u32,
        current_time: u64,       // NEW: Current time from verifier
        window_size: u64         // NEW: Configurable window size (typically 60 seconds)
    ) -> bool {
        // 1. Verify agent is active
        assert_eq(agent_status, 1u8);
        
        // 2. Verify OTP matches expected value
        assert_eq(provided_otp, expected_otp);
        
        // 3. NEW: Implement time window check
        let time_diff: u64 = current_time >= timestamp 
            ? current_time - timestamp 
            : timestamp - current_time;
            
        assert(time_diff <= window_size);
        
        return true;
    }
    
    // NEW: Helper to verify time window only
    transition is_time_valid(
        timestamp: u64,
        current_time: u64,
        window_size: u64
    ) -> bool {
        let time_diff: u64 = current_time >= timestamp 
            ? current_time - timestamp 
            : timestamp - current_time;
            
        return time_diff <= window_size;
    }
}