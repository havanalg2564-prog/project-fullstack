from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    ownerId: int
    createdTime: datetime