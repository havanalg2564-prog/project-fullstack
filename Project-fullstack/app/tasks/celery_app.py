from celery import Celery

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.note import Note
from app.models.user import User
from app.services.notification import createNotification


celeryApp = Celery(
    "notes",
    broker=settings.redisUrl,
    backend=settings.redisUrl,
)


@celeryApp.task
def notifyNoteCreated(noteId: int, ownerId: int) -> dict:
    session = SessionLocal()
    try:
        note = session.get(Note, noteId)
        user = session.get(User, ownerId)
        if not note or not user:
            return {"status": "skipped", "reason": "нет данных"}

        message = f"Создана новая заметка «{note.title}» у пользователя {user.email}"
        createNotification(
            session, ownerId=ownerId, message=message, noteId=noteId
        )
        # Имитация отправки e-mail/пуша
        print(f"[CELERY] Отправлено уведомление: {message}")
        return {"status": "sent", "email": user.email, "message": message}
    finally:
        session.close()