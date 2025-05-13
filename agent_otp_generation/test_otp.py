# Test implementation of the OTP algorithm in Python to verify our Leo code
def generate_otp(timestamp):
    # Use the lowest 6 digits of timestamp as a base
    base_otp = timestamp % 1000000
    
    # Create a modifier based on timestamp
    # Use the tens and ones digits of the minutes to create a shift amount
    minutes = (timestamp // 60) % 100
    shift_amount = minutes % 10  # 0-9 shift
    
    # Apply a circular shift to the digits
    # This is the same logic as in Leo
    factor = 10 ** shift_amount
    rotated = (base_otp % factor) * (1000000 // factor) + (base_otp // factor)
    
    # Final OTP is the rotated value
    otp = rotated % 1000000
    
    # Ensure 6 digits with leading zeros
    return f"{otp:06d}"

# Test the OTP generation with the same timestamp as used in Leo
timestamp = 1747099999
otp = generate_otp(timestamp)
print(f"Timestamp: {timestamp}")
print(f"Minutes: {(timestamp // 60) % 100}")
print(f"Shift amount: {(timestamp // 60) % 100 % 10}")
print(f"Generated OTP: {otp}") 