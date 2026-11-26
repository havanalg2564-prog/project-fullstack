from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import getCurrentUser, requireRole
from app.db.session import getSession
from app.models.user import User, UserRole
from app.schemas.note import NoteCreate, NoteUpdate, NoteRead
from app.services.note import (
    createNote,
    listNotes,
    getNote,
    updateNote,
    deleteNote,
    adminDeleteNote,
)
from app.tasks.celery_app import notifyNoteCreated


router = APIRouter(prefix="/notes", tags=["Заметки"])


@router.post("", response_model=NoteRead, status_code=201)
def createNewNote(
    data: NoteCreate,
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    note = createNote(session, currentUser, data)
    # Запускаем фоновую задачу Celery — она создаст уведомление
    notifyNoteCreated.delay(note.id, currentUser.id)
    return note


@router.get("", response_model=list[NoteRead])
def listMyNotes(
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    return listNotes(session, currentUser)


@router.get("/{noteId}", response_model=NoteRead)
def getOneNote(
    noteId: int,
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    return getNote(session, noteId, currentUser)


@router.patch("/{noteId}", response_model=NoteRead)
def updateOneNote(
    noteId: int,
    data: NoteUpdate,
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    return updateNote(session, noteId, currentUser, data)


@router.delete("/{noteId}", status_code=204)
def deleteOneNote(
    noteId: int,
    currentUser: User = Depends(getCurrentUser),
    session: Session = Depends(getSession),
):
    deleteNote(session, noteId, currentUser)


@router.delete("/admin/{noteId}", status_code=204)
def adminDeleteAnyNote(
    noteId: int,
    currentUser: User = Depends(requireRole(UserRole.ADMIN)),
    session: Session = Depends(getSession),
):
    adminDeleteNote(session, noteId)