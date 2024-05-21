from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()
fernet = Fernet(os.getenv('SECRET_KEY'))

def encryptData(id):
    val = fernet.encrypt(str(id).encode()).decode()
    return val

def decryptData(id):
    val = fernet.decrypt(str(id)).decode()
    return val