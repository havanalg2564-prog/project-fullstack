from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashPassword(password: str) -> str:
    return pwdContext.hash(password)


def verifyPassword(plain: str, hashed: str) -> bool:
    return pwdContext.verify(plain, hashed)


def createAccessToken(userId: int) -> str:
    payload = {
        "sub": str(userId),
        "exp": datetime.utcnow() + timedelta(minutes=settings.accessTokenExpireMinutes),
    }
    return jwt.encode(payload, settings.secretKey, algorithm=settings.algorithm)


def decodeToken(token: str) -> dict:
    return jwt.decode(token, settings.secretKey, algorithms=[settings.algorithm])