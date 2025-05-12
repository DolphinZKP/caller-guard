program agent_otp_proof.aleo {
    // This program verifies that a given OTP is valid for an agent
    // without revealing the agent's private data
    
    // Main verification function for iOS app to check
    transition verify_otp(
        agent_id: field,         // Public input: agent being verified
        timestamp: u64,          // Public input: when OTP was generated
        provided_otp: u32,       // Public input: OTP entered by user
        agent_status: u8,        // Public input: agent's status from record
        expected_otp: u32        // Output from agent_otp_generate
    ) -> bool {
        // 1. Verify agent is active (status == 1)
        assert_eq(agent_status, 1u8);
        
        // 2. Verify OTP matches expected value
        assert_eq(provided_otp, expected_otp);
        
        // 3. Check timestamp is within valid window (optional)
        // In real implementation, you might want to check if timestamp
        // is within acceptable range (e.g., current time window)
        
        // If all checks pass, return true
        return true;
    }
    
    // Helper function to verify just the OTP value
    // This is useful when agent status is verified separately
    transition verify_otp_only(
        provided_otp: u32,
        expected_otp: u32
    ) -> bool {
        return provided_otp == expected_otp;
    }
}