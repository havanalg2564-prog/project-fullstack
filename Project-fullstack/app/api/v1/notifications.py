from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import getCurrentUser
from app.db.session import getSession
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.services.notification import listNotifications


router = APIRouter(prefix="/notifications", tags=["Уведомления"])


@router.get(
    "",
    response_model=list[NotificationRead],
    summary="Мои уведомления",
    description="Возвращает список уведомлений, созданных для текущего пользователя (например, при создании заметки).",
)
def listMyNotifications(
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    return listNotifications(session, currentUser)