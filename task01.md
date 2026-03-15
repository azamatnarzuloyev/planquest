# Task 1: Project Initialization va Monorepo Structure

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 12 qadam
**Dependency:** Yo'q (birinchi task)
**Output:** `docker compose up` bilan backend + frontend + postgres + redis ishga tushadi, `/health` endpoint `{"status": "ok"}` qaytaradi.

---

## Qadamlar

### Qadam 1: Root project structure yaratish
Asosiy papkalar va root fayllar:
```
telegram/
├── backend/
├── frontend/
├── docker/
├── .gitignore
├── .env.example
├── Makefile
└── README.md
```
- `backend/`, `frontend/`, `docker/` papkalarini yaratish
- Root `.gitignore` (Python, Node, Docker, IDE, .env)
- Root `README.md` (loyiha nomi, qisqacha ta'rif, setup instruksiyasi placeholder)

**Tayyor belgisi:** Papkalar mavjud, `.gitignore` to'g'ri ishlaydi.

---

### Qadam 2: Backend — Python project init (FastAPI + uv)
```
backend/
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py          ← FastAPI app instance
│   ├── config.py         ← Settings (pydantic-settings)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py  ← GET /health endpoint
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── core/
│       └── __init__.py
└── tests/
    ├── __init__.py
    └── test_health.py
```

**pyproject.toml dependencies:**
- `fastapi` — web framework
- `uvicorn[standard]` — ASGI server
- `pydantic-settings` — environment variable management
- `asyncpg` — async PostgreSQL driver
- `sqlalchemy[asyncio]` — ORM
- `alembic` — migration tool
- `redis` — Redis client (aioredis)
- `httpx` — async HTTP client (test + Telegram API)
- `python-dotenv` — .env loading

**Dev dependencies:**
- `pytest` — testing
- `pytest-asyncio` — async test support
- `ruff` — linter + formatter

**Tayyor belgisi:** `cd backend && uv sync` dependencies o'rnatadi, xatolik yo'q.

---

### Qadam 3: Backend — FastAPI app va config
**app/config.py:**
```python
# pydantic-settings bilan environment variable'lar
class Settings:
    APP_NAME: str = "PlanQuest"
    DEBUG: bool = False
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:port/db
    REDIS_URL: str     # redis://host:port/0
    BOT_TOKEN: str     # Telegram bot token
    SECRET_KEY: str    # JWT signing key
    CORS_ORIGINS: list[str] = ["*"]
```

**app/main.py:**
```python
# FastAPI instance
# CORS middleware
# Router include (health router)
# Lifespan: startup/shutdown (DB pool, Redis connection)
```

**Tayyor belgisi:** `python -m app.main` xatosiz import bo'ladi (server hali ishga tushmaydi, faqat import test).

---

### Qadam 4: Backend — Health check endpoint
**app/api/routes/health.py:**
```
GET /health → {"status": "ok", "version": "0.1.0"}
GET /health/ready → {"database": "ok", "redis": "ok"} (yoki "error" agar connect bo'lmasa)
```

- `/health` — oddiy liveness check (har doim 200)
- `/health/ready` — readiness check (DB va Redis connectivity tekshiradi)
- Health router `main.py` da include qilinadi

**Tayyor belgisi:** `curl localhost:8000/health` → `{"status": "ok"}` qaytaradi.

---

### Qadam 5: Frontend — Next.js project init
```
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
├── next.config.ts
├── public/
├── src/
│   ├── app/
│   │   ├── layout.tsx      ← Root layout
│   │   ├── page.tsx        ← Home page (placeholder)
│   │   └── globals.css     ← Tailwind imports
│   ├── components/
│   │   └── .gitkeep
│   ├── lib/
│   │   ├── api.ts          ← API client (axios/fetch wrapper)
│   │   └── telegram.ts     ← Telegram SDK helpers (placeholder)
│   └── types/
│       └── index.ts        ← Type definitions (placeholder)
└── .eslintrc.json
```

**Dependencies:**
- `next`, `react`, `react-dom` — framework
- `typescript`, `@types/react`, `@types/node` — types
- `tailwindcss`, `postcss`, `autoprefixer` — styling
- `axios` — HTTP client

**Home page (placeholder):**
- "PlanQuest" sarlavha
- "Mini App loading..." text
- Tailwind styled, centered

**Tayyor belgisi:** `cd frontend && npm run dev` → localhost:3000 da sahifa ochiladi.

---

### Qadam 6: Frontend — API client service
**src/lib/api.ts:**
```typescript
// Base URL: process.env.NEXT_PUBLIC_API_URL yoki /api
// Axios instance with:
//   - baseURL
//   - timeout: 10000ms
//   - interceptor: Authorization header (JWT token qo'shish)
//   - interceptor: error handling (401 → re-auth, 500 → error toast)

// Health check function:
// api.getHealth() → GET /health
```

**src/lib/telegram.ts (placeholder):**
```typescript
// Telegram Mini Apps SDK integration
// initData extraction
// Theme detection
// Viewport setup
// Bu faylga Task 14 da to'liq kod yoziladi
```

**Tayyor belgisi:** API client import qilinganda xatosiz ishlaydi.

---

### Qadam 7: .env.example fayl
```env
# === Database ===
POSTGRES_USER=planquest
POSTGRES_PASSWORD=planquest_secret
POSTGRES_DB=planquest
DATABASE_URL=postgresql+asyncpg://planquest:planquest_secret@postgres:5432/planquest

# === Redis ===
REDIS_URL=redis://redis:6379/0

# === Telegram ===
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# === App ===
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]

# === Frontend ===
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Tayyor belgisi:** `.env.example` barcha kerakli variable'larni o'z ichiga oladi, hech biri real secret emas.

---

### Qadam 8: Docker — Backend Dockerfile
**docker/backend.Dockerfile:**
```dockerfile
# Base: python:3.12-slim
# Working dir: /app
# Copy pyproject.toml → install dependencies (uv yoki pip)
# Copy app/ source code
# Expose 8000
# CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Muhim:**
- Multi-stage build emas (dev uchun oddiy)
- `.dockerignore` — `__pycache__`, `.venv`, `tests/`, `.git`
- Hot-reload uchun volume mount (docker-compose da)

**Tayyor belgisi:** `docker build -f docker/backend.Dockerfile ./backend` xatosiz build bo'ladi.

---

### Qadam 9: Docker — Frontend Dockerfile
**docker/frontend.Dockerfile:**
```dockerfile
# Base: node:20-slim
# Working dir: /app
# Copy package.json, package-lock.json → npm install
# Copy source code
# Expose 3000
# CMD: npm run dev (development mode)
```

**Tayyor belgisi:** `docker build -f docker/frontend.Dockerfile ./frontend` xatosiz build bo'ladi.

---

### Qadam 10: Docker Compose — barcha servislarni birlashtirish
**docker-compose.yml:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment: from .env
    ports: 5432:5432
    volumes: postgres_data:/var/lib/postgresql/data
    healthcheck: pg_isready

  redis:
    image: redis:7-alpine
    ports: 6379:6379
    healthcheck: redis-cli ping

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    ports: 8000:8000
    env_file: .env
    volumes: ./backend/app:/app/app (hot-reload)
    depends_on:
      postgres: condition: service_healthy
      redis: condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend.Dockerfile
    ports: 3000:3000
    env_file: .env
    volumes: ./frontend/src:/app/src (hot-reload)
    depends_on: [backend]

volumes:
  postgres_data:
```

**Tayyor belgisi:** `docker compose up -d` → barcha 4 servis "healthy" / "running" statusida.

---

### Qadam 11: Makefile — dev convenience commands
**Makefile:**
```makefile
# Asosiy komandalar:
up:              docker compose up -d
down:            docker compose down
restart:         docker compose restart
logs:            docker compose logs -f
logs-backend:    docker compose logs -f backend
logs-frontend:   docker compose logs -f frontend

# Database:
db-shell:        docker compose exec postgres psql -U planquest
migrate:         docker compose exec backend alembic upgrade head
migrate-create:  docker compose exec backend alembic revision --autogenerate -m "$(name)"

# Testing:
test:            docker compose exec backend pytest
test-v:          docker compose exec backend pytest -v
lint:            docker compose exec backend ruff check .
format:          docker compose exec backend ruff format .

# Cleanup:
clean:           docker compose down -v --remove-orphans
```

**Tayyor belgisi:** `make up` loyihani ishga tushiradi, `make logs` loglarni ko'rsatadi.

---

### Qadam 12: Verification — hamma narsa ishlayotganini tekshirish
**Tekshirish ro'yxati:**

1. `cp .env.example .env` → `.env` fayl yaratish
2. `make up` → barcha servislar ishga tushadi
3. `docker compose ps` → 4 ta servis "running" yoki "healthy"
4. `curl http://localhost:8000/health` → `{"status": "ok"}`
5. Browser: `http://localhost:3000` → "PlanQuest" placeholder sahifa
6. `docker compose exec postgres psql -U planquest -c "SELECT 1"` → `1` qaytaradi
7. `docker compose exec redis redis-cli ping` → `PONG`
8. `make down` → barcha servislar to'xtaydi

**Agar hamma narsa ishlasa — Task 1 yakunlangan. ✅**

---

## Yakuniy fayl strukturasi (Task 1 tugagandan keyin)

```
telegram/
├── .env.example
├── .gitignore
├── Makefile
├── README.md
├── docker-compose.yml
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── health.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   └── core/
│   │       └── __init__.py
│   └── tests/
│       ├── __init__.py
│       └── test_health.py
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── next.config.ts
│   ├── .eslintrc.json
│   ├── public/
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   └── globals.css
│       ├── components/
│       ├── lib/
│       │   ├── api.ts
│       │   └── telegram.ts
│       └── types/
│           └── index.ts
├── documend.md
├── tasks.md
└── task01.md
```

---

## Eslatmalar

- **Git init** bu task ichida qilinmaydi (user o'zi qiladi yoki keyingi qadamda)
- **Alembic** setup bu taskda yo'q — Task 2 da qilinadi
- **Telegram bot** setup bu taskda yo'q — Task 3 da qilinadi
- **Real database connection** `/health/ready` da test qilinadi, lekin ORM model'lar Task 2 da yoziladi
- Barcha fayllar **minimal lekin ishlaydigan** bo'lishi kerak — placeholder emas, real code
