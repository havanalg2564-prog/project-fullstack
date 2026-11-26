from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hashPassword, verifyPassword, createAccessToken
from app.models.user import User, UserRole
from app.schemas.user import UserRegister


def registerUser(session: Session, data: UserRegister) -> User:
    existing = session.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")

    user = User(
        email=data.email,
        hashedPassword=hashPassword(data.password),
        role=UserRole.USER.value,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticateUser(session: Session, email: str, password: str) -> User | None:
    user = session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if not user:
        return None
    if not verifyPassword(password, user.hashedPassword):
        return None
    return user


def createAccessTokenForUser(user: User) -> str:
    return createAccessToken(user.id)