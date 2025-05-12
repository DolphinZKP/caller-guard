import hashlib
import os


def commit_hash(bank_name, rep_id):
    """
    Prepare values for minting an agent in the Aleo contract
    
    Args:
        salt: Random bytes to use as salt
        bank_name: Name of the bank
        rep_id: Representative ID
        permission: The permission string to hash and store
        
    Returns:
        A tuple of (commit_value, perm_hash) ready for the mint_agent transition
    """
    combined = str(bank_name).encode() + str(rep_id).encode()
    commit_value = int.from_bytes(hashlib.sha256(combined).digest(), 'big') % (2**248)  # Limit to field size
   
    return commit_value

def string_to_number(permission_string):
    """Convert a string to a field-compatible integer value"""
    # Convert string to bytes, then to integer
    return int.from_bytes(permission_string.encode(), 'big') % (2**248)

def number_to_string(field_value):
    """Convert a number back to the original string"""
    # Determine number of bytes needed
    byte_length = (field_value.bit_length() + 7) // 8
    # Convert integer back to bytes, then to string
    try:
        return field_value.to_bytes(byte_length, 'big').decode()
    except UnicodeDecodeError:
        return "Error: Unable to decode properly"



# Example usage:
if __name__ == "__main__":

    bank_name = "Canadian Bank"
    rep_id = "ZZ89W"

    commit = commit_hash(bank_name, rep_id)
    print(f"Commit value: {commit}")

    # Example usage
    permission = "open account, but not deposit"
    field_value = string_to_number(permission)
    print(f"Permission hash: {field_value}")
    print(f"Number back to string: {number_to_string(field_value)}")

    # leo execute mint_agent {commit} {field_value}
    print(f"\nExecute your agent minting with:")
    print(f"leo execute mint_agent {commit} {field_value}")