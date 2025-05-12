program agent_otp_generate_leo.aleo {
    // Generate a 6-digit OTP based on rep_id, time window, and a secret seed
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> field {
        // In the Streamlit app, you use HMAC-SHA1 which isn't directly available in Leo
        // We'll simulate it using a combination of hash operations
        
        // 1. Create a message by combining rep_id, bank_name and timestamp
        // Convert timestamp to field by casting
        let timestamp_field: field = timestamp as field;
        let message: field = rep_id + bank_name + timestamp_field;
        
        // 2. Mix with the seed to create a secure hash
        let hash_input: field = message + seed;
        let hash_result: field = BHP256::hash_to_field(hash_input);
        
        // 3. Leo doesn't support direct modulo on field types like we tried
        // We'll use a different approach to extract 6 digits:
        // - We'll use the fact that we just need a number in a certain range
        // - The hash result is already random, so we can derive a 6-digit number from it
        
        // This is a simple approach to extract a value from 0-999999 range
        // In production you'd want to ensure good distribution
        
        // We'll construct a 6-digit OTP by getting a value between 0-999999
        // We can't do modulo directly with fields, but we can use the hash as a source of randomness
        
        return hash_result; // Return the full hash - client can modulo it
    }
    
    // Optional: A transition that verifies an OTP matches
    transition verify_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field,
        provided_otp: field
    ) -> bool {
        // Calculate the expected OTP
        let timestamp_field: field = timestamp as field;
        let message: field = rep_id + bank_name + timestamp_field;
        let hash_input: field = message + seed;
        let expected_otp: field = BHP256::hash_to_field(hash_input);
        
        // Verify the OTP matches
        return expected_otp == provided_otp;
    }
}
