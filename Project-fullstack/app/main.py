from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.v1 import auth, notes, notifications, users
from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import engine


app = FastAPI(
    title="Сервис Заметок",
    description="API для работы с заметками и уведомлениями",
    version="1.0.0",
    # Включает русский язык для кнопок и интерфейса Swagger UI
    swagger_ui_parameters={"lang": "ru"},
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


@app.get(
    "/health",
    summary="Проверка статуса (Healthcheck)",
    description="Проверяет подключение к PostgreSQL и Redis. Возвращает статус 'healthy' или 'degraded'.",
)
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


# --- Кастомная настройка Swagger для перевода полей логина ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Сервис Заметок",
        version="1.0.0",
        description="API для работы с заметками и уведомлениями",
        routes=app.routes,
    )

    # Ищем схему для эндпоинта /auth/login
    schema_name = "Body_login_api_v1_auth_login_post"
    
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        if schema_name in openapi_schema["components"]["schemas"]:
            login_schema = openapi_schema["components"]["schemas"][schema_name]
            props = login_schema.get("properties", {})
            
            # Переводим стандартные поля
            if "username" in props:
                props["username"]["title"] = "Email (Логин)"
                props["username"]["description"] = "Введите ваш email"
            if "password" in props:
                props["password"]["title"] = "Пароль"
                props["password"]["description"] = "Введите ваш пароль"
                
            # Скрываем ненужные OAuth2-поля, чтобы не путать пользователя
            for field in ["grant_type", "scope", "client_id", "client_secret"]:
                if field in props:
                    del props[field]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Применяем кастомную схему
app.openapi = custom_openapi