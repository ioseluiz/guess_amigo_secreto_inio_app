import os
from cryptography.fernet import Fernet
from django.conf import settings
import base64

# En settings.py you should define ENCRYPTION_KEY
# Generate a key using Fernet.generate_key() and store it securely

def get_cipher():
    key = settings.ENCRYPTION_KEY
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in settings")
    return Fernet(key)

def encrypt_data(data: str) -> str:
    if not data:
        return None
    cipher = get_cipher()
    return cipher.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(token: str) -> str:
    if not encrypt_data:
        return None
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypt_data.encode('utf-8')).decode('utf-8')
    except:
        return "ERROR_DECRYPT"