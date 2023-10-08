from datetime import timedelta, datetime
from typing import Dict
from cryptography.fernet import Fernet

from jose import jwt
from pydantic import BaseModel

from config.config import settings


class TokenService:

    def __init__(self):
        self.config = settings.jwt_config
        self.secret_key = self.config.SECRET_KEY
        self.access_token_lifetime = self.config.ACCESS_TOKEN_LIFETIME
        self.refresh_token_lifetime = self.config.REFRESH_TOKEN_LIFETIME
        self.fernet_key = Fernet.generate_key()  # Generating a key for Fernet
        self.cipher_suite = Fernet(self.fernet_key)

    def create_access_token(self, data: Dict):
        data = self.cipher_suite.encrypt(bytes(str(data), 'utf-8'))
        to_encode = data.copy()
        expire = datetime.utcnow() + self.config.ACCESS_TOKEN_LIFETIME
        to_encode.update({"exp": expire})
        encrypted_payload = self.fernet.encrypt(str(to_encode).encode())
        encoded_jwt = jwt.encode(encrypted_payload, self.secret_key, algorithm=self.config.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        return jwt.decode(token, self.secret_key, algorithms=[self.config.ALGORITHM])

if __name__=="__main__":
    print(Fernet.generate_key())