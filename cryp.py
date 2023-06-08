import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

keymap = {}

def get_key(password: str):
    if password in keymap:
        return keymap[password]
    bpassword = password.encode()
    salt = b'something'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(bpassword))
    keymap[password] = key
    return key


def encrypt(b: bytes, password: str):
    key = get_key(password)
    f = Fernet(key)
    return f.encrypt(b)

def decrypt(b: bytes, password: str):
    key = get_key(password)
    f = Fernet(key)
    return f.decrypt(b)


def main():
    test = "hello"
    password = "somepass"
    print(f"{test = }, {password = }")
    encrypted = encrypt(test.encode(), password)
    print(f"{encrypted = }")
    decrypted = decrypt(encrypted, password)
    print(f"{decrypted = }")

if __name__ == "__main__":
    main()