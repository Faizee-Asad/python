import hashlib
import base64

class LicenseManager:
    """Handles the generation and validation of license keys."""
    SECRET_KEY = "DineDashPOS-Malegaon-Secret-2025"

    @staticmethod
    def generate_signature(key):
        """Generates a SHA256 signature for a given key."""
        return hashlib.sha256((key + LicenseManager.SECRET_KEY).encode()).hexdigest()

    @staticmethod
    def validate_license_key(key):
        """Validates if the provided license key is correct."""
        try:
            # This is a simplified validation for the example.
            # A real system would use more complex public/private key cryptography.
            decoded_key = base64.b64decode(key).decode()
            return decoded_key == "VALID-LICENSE-FOR-DINEDASH"
        except Exception:
            return False
