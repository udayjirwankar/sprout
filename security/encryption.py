from cryptography.fernet import Fernet
import os

KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")


def get_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as file:
            file.write(key)

        return key

    with open(KEY_FILE, "rb") as file:
        return file.read()


fernet = Fernet(get_key())


def encrypt_text(text):
    return fernet.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    return fernet.decrypt(encrypted_text.encode()).decode()
