from datetime import datetime

from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    ownerId: Mapped[int] = mapped_column(
        "owner_id", ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    noteId: Mapped[int | None] = mapped_column("note_id", Integer, nullable=True)
    createdTime: Mapped[datetime] = mapped_column(
        "created_time", DateTime, default=datetime.utcnow
    )

    owner = relationship("User", back_populates="notifications")