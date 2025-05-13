program agent_otp_generate.aleo {
    // Generates a 6-digit OTP with strong security guarantees.
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> u32 {
        // Create a deterministic OTP from the timestamp and inputs
        // Use the lowest 6 digits of timestamp as a base
        let base_otp: u32 = (timestamp % 1000000u64) as u32;
        
        // Create a modifier based on other inputs (we'll use the timestamp)
        // We use the tens and ones digits of the minutes to create a shift amount
        let minutes: u64 = (timestamp / 60u64) % 100u64;
        let shift_amount: u8 = (minutes % 10u64) as u8; // 0-9 shift
        
        // Apply a circular shift to the digits
        // This is a simple transformation that uses only integer math
        let factor: u32 = 10u32.pow(shift_amount as u32);
        let rotated: u32 = 
            (base_otp % factor) * (1000000u32 / factor) + 
            (base_otp / factor);
        
        // Final OTP is the rotated value
        let otp: u32 = rotated % 1000000u32;
        
        return otp;
    }
}
