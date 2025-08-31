import base64

def generate_license_key():
    """
    Generates a valid license key for the DineDash POS application.
    This is a simple key generator based on a predefined string.
    """
    # This is the string the main application expects for a valid license.
    secret_string = "VALID-LICENSE-FOR-DINEDASH"
    
    # Encode the string to bytes, then encode it using base64.
    encoded_bytes = base64.b64encode(secret_string.encode('utf-8'))
    
    # Convert the base64 bytes back to a string to create the final key.
    license_key = encoded_bytes.decode('utf-8')
    
    return license_key

if __name__ == "__main__":
    key = generate_license_key()
    print("="*40)
    print("  DineDash POS License Key Generator")
    print("="*40)
    print("\nGenerated License Key:")
    print(key)
    print("\nCopy this key and provide it to your customer.")
    print("="*40)
