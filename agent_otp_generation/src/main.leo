program agent_otp_generate.aleo {
    // Generate a 6-digit OTP with stronger security guarantees
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> u32 {
        // Use a single hash operation with combined inputs
        let combined: field = rep_id + bank_name + (timestamp as field) + seed;
        let hash_result: field = BHP256::hash_to_field(combined);
        
        // Convert to u32 and limit to 6 digits (0-999999)
        let otp: u32 = (hash_result as u32) % 1000000u32;
        
        return otp;
    }
}