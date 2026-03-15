# Task 2: Database Schema va Migration System

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 8 qadam
**Dependency:** Task 1 ✅
**Output:** `alembic upgrade head` → `users` va `user_settings` jadvallari yaratiladi. SQLAlchemy model'lar ishlaydi.

---

## Qadamlar

### Qadam 1: Alembic konfiguratsiyasi
Backend ichida Alembic init qilish va async PostgreSQL bilan sozlash.

**Yaratiladigan fayllar:**
```
backend/
├── alembic.ini
└── alembic/
    ├── env.py          ← async engine bilan ishlash uchun o'zgartirilgan
    ├── script.py.mako  ← migration template
    └── versions/       ← migration fayllari shu yerda
```

**alembic.ini:**
- `sqlalchemy.url` → `.env` dagi `DATABASE_URL` dan olinadi
- `script_location` → `alembic`

**alembic/env.py:**
- `asyncpg` driver bilan async migration support
- `target_metadata` → SQLAlchemy Base.metadata ga bog'lash
- `run_migrations_online()` → `create_async_engine` ishlatadi
- `.env` dan `DATABASE_URL` o'qiydi

**Tayyor belgisi:** `alembic current` xatosiz ishlaydi (hozircha migration yo'q).

---

### Qadam 2: SQLAlchemy Base model
Barcha model'lar uchun umumiy Base class yaratish.

**backend/app/models/base.py:**
```python
# DeclarativeBase — SQLAlchemy 2.0 style
# Common fields:
#   id: UUID (primary key, server_default=gen_random_uuid())
#   created_at: timestamp with timezone (server_default=now())
#   updated_at: timestamp with timezone (onupdate=now())
```

- UUID primary key — distributed system uchun tayyorgarlik
- `created_at` va `updated_at` har bir jadvalda avtomatik
- `Base` class — barcha model'lar shudan meros oladi

**Tayyor belgisi:** `from app.models.base import Base` import xatosiz ishlaydi.

---

### Qadam 3: User model
**backend/app/models/user.py:**

```
users jadvali:
┌──────────────────┬───────────────────┬─────────────────────────────┐
│ Column           │ Type              │ Constraints                 │
├──────────────────┼───────────────────┼─────────────────────────────┤
│ id               │ UUID              │ PK, default gen_random_uuid │
│ telegram_id      │ BIGINT            │ UNIQUE, NOT NULL, INDEX     │
│ first_name       │ VARCHAR(255)      │ NOT NULL                    │
│ last_name        │ VARCHAR(255)      │ nullable                    │
│ username         │ VARCHAR(255)      │ nullable                    │
│ segment          │ VARCHAR(50)       │ nullable (student, freelancer, entrepreneur, developer, other) │
│ timezone         │ VARCHAR(50)       │ default 'UTC'               │
│ language         │ VARCHAR(10)       │ default 'uz'                │
│ is_premium       │ BOOLEAN           │ default false               │
│ is_active        │ BOOLEAN           │ default true                │
│ onboarding_step  │ INTEGER           │ default 0 (0=not started, 1=segment, 2=first_task, 3=reminder, 4=done) │
│ referral_code    │ VARCHAR(20)       │ UNIQUE                      │
│ referred_by      │ UUID              │ FK → users.id, nullable     │
│ created_at       │ TIMESTAMPTZ       │ server default now()        │
│ updated_at       │ TIMESTAMPTZ       │ onupdate now()              │
└──────────────────┴───────────────────┴─────────────────────────────┘
```

**Indexlar:**
- `ix_users_telegram_id` — tez lookup (har bir bot request da ishlatiladi)
- `ix_users_referral_code` — referral link tekshirish

**Tayyor belgisi:** Model import qilinganda xatosiz ishlaydi.

---

### Qadam 4: UserSettings model
**backend/app/models/user_settings.py:**

```
user_settings jadvali:
┌──────────────────────┬───────────────────┬─────────────────────────────┐
│ Column               │ Type              │ Constraints                 │
├──────────────────────┼───────────────────┼─────────────────────────────┤
│ id                   │ UUID              │ PK                          │
│ user_id              │ UUID              │ FK → users.id, UNIQUE       │
│ morning_reminder_time│ TIME              │ default '08:00'             │
│ evening_reminder_time│ TIME              │ default '21:00'             │
│ quiet_hours_start    │ TIME              │ default '23:00'             │
│ quiet_hours_end      │ TIME              │ default '07:00'             │
│ theme                │ VARCHAR(20)       │ default 'system' (light/dark/system) │
│ daily_message_count  │ INTEGER           │ default 0 (anti-spam uchun, har kuni reset) │
│ max_daily_messages   │ INTEGER           │ default 6                   │
│ created_at           │ TIMESTAMPTZ       │ server default now()        │
│ updated_at           │ TIMESTAMPTZ       │ onupdate now()              │
└──────────────────────┴───────────────────┴─────────────────────────────┘
```

**Relationship:**
- `User` → `UserSettings` (one-to-one)
- `user_settings.user_id` → `users.id` (ON DELETE CASCADE)

**Tayyor belgisi:** `User.settings` relationship ishlaydi.

---

### Qadam 5: Models __init__.py — barcha model'larni export qilish
**backend/app/models/__init__.py:**
```python
from app.models.base import Base
from app.models.user import User
from app.models.user_settings import UserSettings

__all__ = ["Base", "User", "UserSettings"]
```

Bu fayl Alembic `env.py` da `target_metadata = Base.metadata` ishlashi uchun zarur — barcha model'lar import qilinishi kerak shunda Alembic ularni "ko'radi".

**Tayyor belgisi:** `from app.models import Base, User, UserSettings` xatosiz ishlaydi.

---

### Qadam 6: Pydantic schemas (User uchun)
**backend/app/schemas/user.py:**

```python
# UserBase — umumiy fieldlar
#   first_name: str
#   last_name: str | None
#   username: str | None

# UserCreate — yangi user yaratish (internal, bot dan keladi)
#   telegram_id: int
#   first_name: str
#   ...

# UserResponse — API response
#   id: UUID
#   telegram_id: int
#   first_name, last_name, username
#   segment, timezone, language
#   is_premium, onboarding_step
#   referral_code
#   created_at

# UserUpdate — user ma'lumotlarini yangilash
#   segment: str | None
#   timezone: str | None
#   language: str | None

# UserSettingsResponse — settings response
#   morning_reminder_time, evening_reminder_time
#   quiet_hours_start, quiet_hours_end
#   theme

# UserSettingsUpdate — settings yangilash
#   morning_reminder_time: time | None
#   evening_reminder_time: time | None
#   ...
```

**Tayyor belgisi:** Pydantic schema'lar import qilinganda validation ishlaydi.

---

### Qadam 7: Birinchi migration yaratish va ishga tushirish
Alembic bilan `users` va `user_settings` jadvallarini yaratish.

**Qadamlar:**
1. `alembic revision --autogenerate -m "create users and user_settings"` → migration fayl yaratadi
2. Migration faylni tekshirish — to'g'ri `CREATE TABLE` borligini confirm qilish
3. `alembic upgrade head` → jadvallar yaratiladi
4. `psql` orqali tekshirish: `\dt` → `users`, `user_settings` ko'rinadi

**Tayyor belgisi:**
- `alembic upgrade head` xatosiz ishlaydi
- `SELECT * FROM users` → bo'sh jadval (xato emas)
- `SELECT * FROM user_settings` → bo'sh jadval
- `alembic current` → head revision ko'rsatadi

---

### Qadam 8: Verification — hamma narsa ishlayotganini tekshirish
**Tekshirish ro'yxati:**

1. `docker-compose exec -T backend alembic current` → current revision ko'rsatadi
2. `docker-compose exec -T postgres psql -U planquest -c "\dt"` → `users`, `user_settings`, `alembic_version` jadvallari bor
3. `docker-compose exec -T postgres psql -U planquest -c "\d users"` → barcha column'lar to'g'ri type bilan
4. `docker-compose exec -T postgres psql -U planquest -c "\d user_settings"` → FK va column'lar to'g'ri
5. `docker-compose exec -T postgres psql -U planquest -c "SELECT * FROM users"` → bo'sh jadval, xato yo'q
6. Backend restart qilganda xatolik yo'q: `docker-compose restart backend`
7. `curl localhost:8000/health/ready` → `{"status":"ok","database":"ok","redis":"ok"}`

**Agar hamma narsa ishlasa — Task 2 yakunlangan. ✅**

---

## Eslatmalar

- **UUID** primary key ishlatamiz (auto-increment emas) — distributed system uchun tayyorgarlik, Telegram bot ID bilan aralashmaslik uchun
- **telegram_id** `BIGINT` bo'lishi kerak (Telegram user ID 10+ raqamli bo'lishi mumkin)
- **onboarding_step** — user qaysi onboarding bosqichida ekanini track qiladi (Task 13 da ishlatiladi)
- **referral_code** — Task 28 da to'liq ishlatiladi, lekin jadvalda hozirdan tayyorlab qo'yamiz
- **daily_message_count** — anti-spam uchun, reminder engine (Task 12) da ishlatiladi
- Model'larga keyingi task'larda yangi jadvallar qo'shiladi (tasks, habits, focus_sessions, va h.k.) — har biri alohida migration
