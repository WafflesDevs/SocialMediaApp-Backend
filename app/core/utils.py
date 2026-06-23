from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=[f"{settings.encryption}"],deprecated="auto") #Hashing algo for passwords!


def hash(password):
    return pwd_context.hash(password)

def verify(plain_password,hash_password):
    return pwd_context.verify(plain_password,hash_password)
