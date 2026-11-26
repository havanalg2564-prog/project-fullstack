from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import requireRole
from app.db.session import getSession
from app.models.user import User, UserRole
from app.schemas.user import UserRead


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("", response_model=list[UserRead])
def adminListUsers(
    currentUser: User = Depends(requireRole(UserRole.ADMIN)),
    session: Session = Depends(getSession),
):
    return list(session.execute(select(User)).scalars().all())