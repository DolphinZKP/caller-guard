program agent_otp_generate.aleo {
    // Generate a 6-digit OTP with stronger security guarantees
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> u32 {
        // Convert timestamp to field
        let timestamp_field: field = timestamp as field;
        
        // Apply multiple hashing rounds for security
        let hash1: field = BHP256::hash_to_field(rep_id + seed);
        let hash2: field = BHP256::hash_to_field(bank_name + hash1);
        let hash3: field = BHP256::hash_to_field(timestamp_field + hash2);
        
        // Convert hash to u128 for numeric operations
        let hash_u128: u128 = hash3 as u128;
        
        // Extract 6 digits (0-999999) using modulo
        let six_digits: u32 = (hash_u128 % 1000000u128) as u32;
        
        return six_digits;
    }
}