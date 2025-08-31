import base64

# This script generates a valid license key for the DineDash POS application.
# You can run this script to create keys to give to your customers.

# The phrase to be encoded. This must match the phrase in main.py
SECRET_PHRASE = "VALID-LICENSE-FOR-DINEDASH"

def generate_key():
    """Encodes the secret phrase into a license key."""
    encoded_bytes = base64.b64encode(SECRET_PHRASE.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

if __name__ == "__main__":
    license_key = generate_key()
    print("=====================================")
    print("  DineDash POS License Key Generator")
    print("=====================================")
    print(f"\nYour new license key is:\n\n{license_key}\n")
    print("Provide this key to your customer for activation.")
    print("=====================================")

