import enum
from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashedPassword: Mapped[str] = mapped_column("hashed_password", String(255))
    role: Mapped[str] = mapped_column(String(32), default=UserRole.USER.value)
    createdTime: Mapped[datetime] = mapped_column(
        "created_time", DateTime, default=datetime.utcnow
    )

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship(
        "Notification", back_populates="owner", cascade="all, delete-orphan"
    )