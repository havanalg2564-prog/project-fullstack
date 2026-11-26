import os

# Отключаем rate limiting в тестах до импорта приложения
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only")
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import getSession
from app.main import app
from app.core.limiter import limiter


limiter.enabled = False

# SQLite in-memory + StaticPool = одна БД на все соединения
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)


def overrideGetSession():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setupDb():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[getSession] = overrideGetSession
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def updateDb():
    """Короткая транзакция для подготовки данных в тестах."""

    def run(func):
        session = TestingSessionLocal()
        try:
            func(session)
            session.commit()
        finally:
            session.close()

    return run