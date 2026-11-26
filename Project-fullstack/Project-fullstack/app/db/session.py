from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


engine = create_engine(
    settings.databaseUrl.replace("postgres://", "postgresql://"),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def getSession() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()