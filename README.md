# PlanQuest — Gamified Productivity Planner for Telegram

Telegram Bot + Mini App platformasida ishlaydigan gamified productivity planner.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Infrastructure:** Docker, Docker Compose

## Quick Start

```bash
# 1. Environment sozlash
cp .env.example .env

# 2. Loyihani ishga tushirish
make up

# 3. Tekshirish
curl http://localhost:8000/health
# Browser: http://localhost:3000
```

## Development Commands

```bash
make up              # Barcha servislarni ishga tushirish
make down            # To'xtatish
make logs            # Loglarni ko'rish
make test            # Testlarni ishga tushirish
make migrate         # Database migration
make lint            # Linter
```
