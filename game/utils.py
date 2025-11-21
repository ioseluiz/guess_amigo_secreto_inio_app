import os
from cryptography.fernet import Fernet
from django.conf import settings

def get_cipher():
    key = settings.ENCRYPTION_KEY # Asegúrate de tener esto en settings.py
    return Fernet(key)

def encrypt_data(data: str) -> str:
    if not data:
        return None
    cipher = get_cipher()
    return cipher.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(token: str) -> str:
    # 1. Verificar el token, no la función
    if not token: 
        return None
    cipher = get_cipher()
    try:
        # 2. Usar la variable 'token'
        return cipher.decrypt(token.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Error desencriptando: {e}") # Útil para debug
        return "ERROR_DECRYPT"