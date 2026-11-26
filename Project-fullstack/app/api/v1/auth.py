from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import getCurrentUser
from app.core.limiter import limiter
from app.db.session import getSession
from app.schemas.user import UserRegister, UserRead, Token
from app.services.auth import (
    registerUser,
    authenticateUser,
    createAccessTokenForUser,
)


router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserRegister, session: Session = Depends(getSession)):
    return registerUser(session, data)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    formData: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(getSession),
):
    user = authenticateUser(session, formData.username, formData.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return Token(accessToken=createAccessTokenForUser(user))


@router.get("/me", response_model=UserRead)
def readMe(currentUser=Depends(getCurrentUser)):
    return currentUser