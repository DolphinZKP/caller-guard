program agent_otp_generate.aleo {

    // Internal function to generate OTP - used by both transitions
    function internal_generate_otp(timestamp: u64) -> u32 {
        // Create a deterministic OTP from the timestamp
        // Use the lowest 6 digits of timestamp as a base
        let base_otp: u32 = (timestamp % 1000000u64) as u32;
        
        // Create a modifier based on timestamp
        // We use the tens and ones digits of the minutes to create a shift amount
        let minutes: u64 = (timestamp / 60u64) % 100u64;
        let shift_amount: u8 = (minutes % 10u64) as u8; // 0-9 shift
        
        // Apply a circular shift to the digits
        let factor: u32 = 10u32.pow(shift_amount as u32);
        let rotated: u32 = 
            (base_otp % factor) * (1000000u32 / factor) + 
            (base_otp / factor);
        
        // Final OTP is the rotated value
        let otp: u32 = rotated % 1000000u32;
        
        return otp;
    }

    // Public transition for generating OTP
    transition generate_otp(
        rep_id: field,
        bank_name: field,
        timestamp: u64,
        seed: field
    ) -> u32 {
        // Call internal logic
        let otp: u32 = internal_generate_otp(timestamp);
        return otp;
    }

    // ZK-SNARK transition for proving OTP generation
    // not actual proof by  leo run prove_otp_generation "1233field" "5678field" "123field" "1747100401u64" "100401u32"
    transition prove_otp_generation(
        private rep_id: field,
        private bank_name: field,
        private seed: field,
        public timestamp: u64,
        public otp: u32
    ) -> bool {
        // Call internal logic to compute OTP
        let computed: u32 = internal_generate_otp(timestamp);

        // Enforce that the provided OTP matches the computed one
        assert(computed == otp);

        return true;
    }
}


   