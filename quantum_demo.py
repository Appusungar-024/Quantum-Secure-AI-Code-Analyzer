from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def classical_alice_bob():
    print("\n🔴 Classical Communication (NOT Quantum Safe)\n")

    # Bob generates key pair
    key = RSA.generate(2048)
    public_key = key.publickey()

    # Alice encrypts message
    message = b"Hello Bob, this is Alice"
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(message)

    print("Encrypted message:", encrypted)

    # Bob decrypts
    cipher = PKCS1_OAEP.new(key)
    decrypted = cipher.decrypt(encrypted)

    print("Decrypted message:", decrypted.decode())

    return {
        "type": "RSA",
        "encrypted": str(encrypted),
        "decrypted": decrypted.decode()
    }