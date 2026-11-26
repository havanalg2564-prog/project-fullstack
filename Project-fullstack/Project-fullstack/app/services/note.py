from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate


def createNote(session: Session, owner: User, data: NoteCreate) -> Note:
    note = Note(title=data.title, body=data.body, ownerId=owner.id)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def listNotes(session: Session, owner: User) -> list[Note]:
    rows = (
        session.execute(
            select(Note)
            .where(Note.ownerId == owner.id)
            .order_by(Note.createdTime.desc())
        )
        .scalars()
        .all()
    )
    return list(rows)


def getNote(session: Session, noteId: int, owner: User) -> Note:
    note = session.get(Note, noteId)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    if note.ownerId != owner.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заметке")
    return note


def updateNote(
    session: Session, noteId: int, owner: User, data: NoteUpdate
) -> Note:
    note = getNote(session, noteId, owner)
    if data.title is not None:
        note.title = data.title
    if data.body is not None:
        note.body = data.body
    session.commit()
    session.refresh(note)
    return note


def deleteNote(session: Session, noteId: int, owner: User) -> None:
    note = getNote(session, noteId, owner)
    session.delete(note)
    session.commit()


def adminDeleteNote(session: Session, noteId: int) -> None:
    note = session.get(Note, noteId)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    session.delete(note)
    session.commit()