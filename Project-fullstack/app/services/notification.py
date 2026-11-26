from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def listNotifications(session: Session, owner: User) -> list[Notification]:
    rows = (
        session.execute(
            select(Notification)
            .where(Notification.ownerId == owner.id)
            .order_by(Notification.createdTime.desc())
        )
        .scalars()
        .all()
    )
    return list(rows)


def createNotification(
    session: Session,
    ownerId: int,
    message: str,
    noteId: int | None = None,
) -> Notification:
    notification = Notification(
        message=message, ownerId=ownerId, noteId=noteId
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification