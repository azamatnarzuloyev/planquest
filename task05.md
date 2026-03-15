# Task 5: Task Engine — CRUD API

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 7 qadam
**Dependency:** Task 4 ✅
**Output:** `POST/GET/PATCH/DELETE /api/tasks` ishlaydi. Task yaratish, filterlash, yangilash, archive qilish mumkin.

---

## Qadamlar

### Qadam 1: Task model va migration
**backend/app/models/task.py:**

```
tasks jadvali:
┌────────────────────┬───────────────────┬─────────────────────────────────┐
│ Column             │ Type              │ Constraints                     │
├────────────────────┼───────────────────┼─────────────────────────────────┤
│ id                 │ UUID              │ PK                              │
│ user_id            │ UUID              │ FK → users.id, NOT NULL, INDEX  │
│ title              │ VARCHAR(200)      │ NOT NULL, min 3 char            │
│ notes              │ TEXT              │ nullable                        │
│ planned_date       │ DATE              │ NOT NULL                        │
│ due_date           │ DATE              │ nullable                        │
│ priority           │ VARCHAR(20)       │ NOT NULL, default 'medium'      │
│                    │                   │ (low, medium, high, critical)   │
│ difficulty         │ VARCHAR(20)       │ NOT NULL, default 'medium'      │
│                    │                   │ (trivial, easy, medium, hard, epic) │
│ estimated_minutes  │ INTEGER           │ nullable                        │
│ category           │ VARCHAR(50)       │ nullable                        │
│ goal_id            │ UUID              │ FK → goals.id, nullable (Task 27) │
│ status             │ VARCHAR(20)       │ NOT NULL, default 'pending'     │
│                    │                   │ (pending, completed, skipped, archived) │
│ recurrence_rule    │ VARCHAR(100)      │ nullable (RRULE format)         │
│ source             │ VARCHAR(20)       │ default 'mini_app'              │
│                    │                   │ (bot, mini_app, ai_plan)        │
│ completed_at       │ TIMESTAMPTZ       │ nullable                        │
│ xp_awarded         │ INTEGER           │ default 0                       │
│ created_at         │ TIMESTAMPTZ       │ server default now()            │
│ updated_at         │ TIMESTAMPTZ       │ onupdate now()                  │
└────────────────────┴───────────────────┴─────────────────────────────────┘
```

**Indexlar:**
- `ix_tasks_user_id` — user bo'yicha tez qidirish
- `ix_tasks_user_planned_date` — composite index (user_id + planned_date) — eng ko'p ishlatiladigan query
- `ix_tasks_status` — status bo'yicha filter

**Tayyor belgisi:** `alembic upgrade head` → `tasks` jadvali yaratiladi.

---

### Qadam 2: Pydantic schemas
**backend/app/schemas/task.py:**

```python
# TaskCreate:
#   title: str (min 3, max 200)
#   notes: str | None
#   planned_date: date
#   due_date: date | None
#   priority: enum (low/medium/high/critical), default medium
#   difficulty: enum (trivial/easy/medium/hard/epic), default medium
#   estimated_minutes: int | None
#   category: str | None
#   source: enum (bot/mini_app/ai_plan), default mini_app

# TaskUpdate:
#   title: str | None
#   notes: str | None
#   planned_date: date | None
#   due_date: date | None
#   priority: str | None
#   difficulty: str | None
#   estimated_minutes: int | None
#   category: str | None

# TaskResponse:
#   id, user_id, title, notes, planned_date, due_date,
#   priority, difficulty, estimated_minutes, category,
#   status, source, completed_at, xp_awarded,
#   created_at, updated_at
```

**Tayyor belgisi:** Schema'lar import qilinganda validation ishlaydi.

---

### Qadam 3: Task service — DB operations
**backend/app/services/task_service.py:**

```python
# create_task(db, user_id, data: TaskCreate) → Task
# get_task_by_id(db, task_id, user_id) → Task | None
# get_tasks(db, user_id, date, status, limit, offset) → list[Task]
# update_task(db, task, data: TaskUpdate) → Task
# archive_task(db, task) → Task (status → archived)
```

**Filterlash:**
- `date` — planned_date bo'yicha (aniq kun)
- `status` — pending/completed/skipped/archived
- `priority` — low/medium/high/critical
- default: `status=pending`, `limit=50`
- sort: `planned_date ASC, priority DESC`

**Tayyor belgisi:** Service funksiyalari ishlaydi.

---

### Qadam 4: API endpoints
**backend/app/api/routes/tasks.py:**

```
POST   /api/tasks              → TaskResponse (201)
GET    /api/tasks               → list[TaskResponse] (query params: date, status, priority, limit, offset)
GET    /api/tasks/{id}          → TaskResponse
PATCH  /api/tasks/{id}          → TaskResponse
DELETE /api/tasks/{id}          → {"ok": true} (soft delete → archive)
```

**Muhim:**
- Barcha endpoint'lar `get_current_user` bilan protected
- User faqat o'z task'larini ko'radi/edit qiladi
- Boshqa user'ning task'iga kirsa → 404 (403 emas — security)

**Tayyor belgisi:** CRUD endpoint'lar ishlaydi.

---

### Qadam 5: Models __init__.py yangilash + main.py router qo'shish
- `app/models/__init__.py` ga `Task` import qo'shish
- `app/main.py` ga tasks router include qilish

**Tayyor belgisi:** Server xatosiz start bo'ladi, `/api/tasks` endpoint'lar mavjud.

---

### Qadam 6: Testlar
**backend/tests/test_tasks.py:**

```
# Test 1: POST /api/tasks — task yaratish → 201
# Test 2: GET /api/tasks — user task'larini olish → 200
# Test 3: GET /api/tasks?date=2026-03-16 — date filter
# Test 4: GET /api/tasks/{id} — bitta task
# Test 5: PATCH /api/tasks/{id} — title yangilash
# Test 6: DELETE /api/tasks/{id} — archive
# Test 7: GET /api/tasks/{id} boshqa user → 404
# Test 8: POST /api/tasks — title 2 char → 422 validation error
```

---

### Qadam 7: Verification
1. Backend xatosiz start
2. `POST /api/tasks` → task yaratiladi (201)
3. `GET /api/tasks` → task ro'yxati
4. `GET /api/tasks?date=2026-03-16` → filter ishlaydi
5. `PATCH /api/tasks/{id}` → yangilanadi
6. `DELETE /api/tasks/{id}` → archived bo'ladi
7. DB da task'lar to'g'ri saqlanganini tekshirish

**Agar hamma narsa ishlasa — Task 5 yakunlangan. ✅**
