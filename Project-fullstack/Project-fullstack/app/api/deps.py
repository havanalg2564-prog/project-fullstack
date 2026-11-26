from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decodeToken
from app.db.session import getSession
from app.models.user import User, UserRole


oauth2Scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", auto_error=False
)


def getCurrentUser(
    token: str | None = Depends(oauth2Scheme),
    session: Session = Depends(getSession),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decodeToken(token)
        userId = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = session.get(User, userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def requireRole(*allowedRoles: UserRole):
    def checker(currentUser: User = Depends(getCurrentUser)) -> User:
        if currentUser.role not in [r.value for r in allowedRoles]:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return currentUser

    return checker