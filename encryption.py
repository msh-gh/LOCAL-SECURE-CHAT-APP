from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

class RSAEncryption:
    def __init__(self):
        # Generate RSA key pair (2048 bits is standard secure size)
        self.key_pair = RSA.generate(2048)
        self.private_key = self.key_pair.export_key()
        self.public_key = self.key_pair.publickey().export_key()

    def encrypt_message(self, message: str, recipient_public_key: bytes) -> str:
        """
        Encrypt a message using the recipient's public key.
        Returns the encrypted message in base64 encoded string format.
        """
        recipient_key = RSA.import_key(recipient_public_key)
        cipher = PKCS1_OAEP.new(recipient_key)
        encrypted_bytes = cipher.encrypt(message.encode('utf-8'))
        encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        return encrypted_base64

    def decrypt_message(self, encrypted_message_base64: str) -> str:
        """
        Decrypt a base64 encoded encrypted message using own private key.
        """
        encrypted_bytes = base64.b64decode(encrypted_message_base64.encode('utf-8'))
        private_key = RSA.import_key(self.private_key)
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_message = cipher.decrypt(encrypted_bytes).decode('utf-8')
        return decrypted_message

    def get_public_key(self) -> bytes:
        return self.public_key

    def get_private_key(self) -> bytes:
        return self.private_key

if __name__ == "__main__":
    alice = RSAEncryption()
    bob = RSAEncryption()

    # Alice wants to send a message to Bob
    original_message = "csk srh"
    encrypted = alice.encrypt_message(original_message, bob.get_public_key())
    print("Encrypted:", encrypted)

    # Bob decrypts the message using his private key
    decrypted = bob.decrypt_message(encrypted)
    print("Decrypted:", decrypted)
