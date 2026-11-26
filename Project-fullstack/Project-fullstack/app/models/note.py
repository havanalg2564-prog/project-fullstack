from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="")
    ownerId: Mapped[int] = mapped_column(
        "owner_id", ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    createdTime: Mapped[datetime] = mapped_column(
        "created_time", DateTime, default=datetime.utcnow
    )

    owner = relationship("User", back_populates="notes")