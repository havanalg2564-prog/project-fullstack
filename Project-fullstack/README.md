# Notes Service

Сервис заметок с уведомлениями: FastAPI + SQLAlchemy + PostgreSQL + Redis + Celery + JWT + RBAC + rate limiting + Docker + CI.

**Публичный адрес**: _заполнить после деплоя_ — например, `https://notes-service-production.up.railway.app`

---

## Возможности

- **auth**: регистрация (bcrypt), вход по OAuth2 Password Flow (JWT), `GET /me`, admin-эндпоинт `GET /users`.
- **notes**: CRUD заметок, привязанных к пользователю; при создании запускается Celery-задача, которая пишет уведомление и «отправляет» письмо в лог.
- **notifications**: список уведомлений текущего пользователя.
- **RBAC**: роль `admin` (эндпоинты `GET /api/v1/users`, `DELETE /api/v1/notes/admin/{noteId}`).
- **CORS**: origin задаётся `CORS_ORIGINS`.
- **Rate limiting**: `/auth/login` ограничен 5 запросами в минуту (slowapi).
- **Alembic**: миграции применяются автоматически при старте контейнера.
- **Healthcheck**: `/health` проверяет PostgreSQL и Redis.

---

## Переменные окружения

| Переменная | Назначение | Пример |
|---|---|---|
| `DATABASE_URL` | строка подключения к PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | брокер и backend Celery | `redis://default:pass@host:6379/0` |
| `SECRET_KEY` | секрет для подписи JWT | `openssl rand -hex 32` |
| `ALGORITHM` | алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | время жизни токена | `30` |
| `CORS_ORIGINS` | origin'ы через запятую | `http://localhost:3000,https://app.example.com` |
| `PORT` | порт (Railway задаёт сам) | `8000` |

Секреты хранить **только** в `.env` или в переменных платформы. Файл `.env` в git не коммитится.

Скопируйте шаблон: `cp .env.example .env`.

---

## Локальный запуск через Docker Compose

Одна команда поднимает всё: PostgreSQL, Redis, FastAPI, Celery worker.

```bash
docker compose up --build
```

- API: <http://localhost:8000>  
- Документация Swagger: <http://localhost:8000/docs>  
- Healthcheck: <http://localhost:8000/health>  
- Порядок старта: `db` → `redis` → `api` (применяет миграции) → `worker`.  

Остановить: `docker compose down`, удалить данные БД: `docker compose down -v`.

---

## Локальный запуск без Docker (опционально)

```bash
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
celery -A app.tasks.celery_app.celeryApp worker --loglevel=info
```

---

## Тесты

```bash
pip install -r requirements.txt
pytest -v
```

Тесты используют SQLite in-memory, реальные секреты не требуются. В CI (`.github/workflows/ci.yml`) запускаются автоматически на каждый push.

---

## Деплой на Railway

1. **Создать проект** на <https://railway.app>, подключить GitHub-репозиторий.
2. **Добавить плагины**: `PostgreSQL` и `Redis` (`+ New` → `Database`). Railway создаст переменные `DATABASE_URL` и `REDIS_URL`.
3. **Сервис API**:
   - Source: тот же репозиторий;
   - Builder: `Dockerfile` (Railway определит по `railway.toml`);
   - Variables: `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `CORS_ORIGINS`;
   - Railway сам подставит `DATABASE_URL`, `REDIS_URL`, `PORT`;
   - Healthcheck: `/health` (уже задан в `railway.toml`);
   - `CMD` из Dockerfile выполнит `alembic upgrade head` перед стартом.
4. **Сервис Worker** — второй сервис в том же проекте:
   - Source: тот же репозиторий, тот же Dockerfile;
   - **Start Command** переопределить на:
     ```
     celery -A app.tasks.celery_app.celeryApp worker --loglevel=info --concurrency=2
     ```
   - Variables — те же, что у API;
   - Public domain **не** включать.
5. **Публичный адрес**: в настройках сервиса API → `Settings` → `Networking` → `Generate Domain`. Полученный URL вписать в блок «Публичный адрес» выше.

### Как выдать пользователю роль admin

После регистрации через API:

```sql
-- в сервисе PostgreSQL Railway (Data → Query)
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

---

## Деплой на VPS через docker compose

```bash
git clone <repo> notes-service && cd notes-service
cp .env.example .env
# в .env заменить SECRET_KEY, пароли БД/Redis, CORS_ORIGINS
docker compose up -d --build
```

Публичный адрес — IP сервера и порт `8000`, либо поставьте reverse-proxy (nginx/caddy) с TLS.

---

## API — примеры

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}'
```

### Вход (OAuth2 Password Flow)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=secret123"
```

Ответ: `{"accessToken":"<JWT>","tokenType":"bearer"}`.

### Текущий пользователь

```bash
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer <JWT>"
```

### Создать заметку (запускает Celery-задачу)

```bash
curl -X POST http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Купить молоко","body":"Не забыть про хлеб"}'
```

В логах воркера появится:
`[CELERY] Отправлено уведомление: Создана новая заметка «Купить молоко» у пользователя alice@example.com`.

### Свои заметки и уведомления

```bash
curl http://localhost:8000/api/v1/notes -H "Authorization: Bearer <JWT>"
curl http://localhost:8000/api/v1/notifications -H "Authorization: Bearer <JWT>"
```

### Admin

```bash
curl http://localhost:8000/api/v1/users -H "Authorization: Bearer <ADMIN_JWT>"
curl -X DELETE http://localhost:8000/api/v1/notes/admin/42 -H "Authorization: Bearer <ADMIN_JWT>"
```

### Healthcheck

```bash
curl http://localhost:8000/health
```