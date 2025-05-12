program agent_otp_generate_leo.aleo {
    // Generate a 6-digit OTP based on rep_id, bank_name, timestamp, and seed
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> field {
        // Convert timestamp to field by casting
        let timestamp_field: field = timestamp as field;
        
        // Create a message by combining rep_id, bank_name and timestamp
        let message: field = rep_id + bank_name + timestamp_field;
        
        // Mix with the seed to create a secure hash
        let hash_input: field = message + seed;
        let hash_result: field = BHP256::hash_to_field(hash_input);
        
        // Return the hash for client-side processing into 6 digits
        return hash_result;
    }
}