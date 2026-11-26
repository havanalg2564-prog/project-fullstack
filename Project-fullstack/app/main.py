from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.v1 import auth, notes, notifications, users
from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import engine


app = FastAPI(
    title="Notes Service",
    description="Сервис заметок с уведомлениями",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.corsOrigins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/health")
def health():
    dbOk = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            dbOk = True
    except Exception:
        pass

    redisOk = False
    try:
        import redis

        r = redis.from_url(settings.redisUrl)
        redisOk = r.ping()
    except Exception:
        pass

    overall = "healthy" if (dbOk and redisOk) else "degraded"
    return {"status": overall, "db": dbOk, "redis": redisOk}