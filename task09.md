# Task 9: Streak System

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 7 qadam
**Dependency:** Task 8 ✅
**Output:** Activity streak har bir meaningful action'da yangilanadi. Habit streak per-habit hisoblanadi. Milestone'larda coins reward beriladi. `GET /api/streaks` barcha streak'larni ko'rsatadi.

---

## PRD Reference (documend.md Section 6.4)

**Streak types:**
| Streak | Qualification |
|--------|--------------|
| Activity | Kamida 1 meaningful action (task complete / habit log / focus complete) |
| Habit | Per-habit — ketma-ket completed kunlar |
| Focus | Kamida 1 focus session (Task 10 da to'liq integratsiya) |
| Planning | Morning plan ko'rilgan (Task 12 da integratsiya) |

**Milestone rewards:**
| Kunlar | Coins |
|--------|-------|
| 3 | — (faqat XP bonus) |
| 7 | +25 |
| 14 | +50 |
| 30 | +100 |
| 60 | +200 |
| 90 | +300 |
| 180 | +500 |
| 365 | +1000 |

---

## Qadamlar

### Qadam 1: Streak model va migration
**backend/app/models/streak.py:**

```
streaks jadvali:
┌──────────────────┬───────────────────┬────────────────────────────────┐
│ Column           │ Type              │ Constraints                    │
├──────────────────┼───────────────────┼────────────────────────────────┤
│ id               │ UUID              │ PK                             │
│ user_id          │ UUID              │ FK → users.id, NOT NULL, INDEX │
│ type             │ VARCHAR(50)       │ NOT NULL                       │
│                  │                   │ "activity", "focus", "planning"│
│                  │                   │ yoki "habit_{uuid}" format     │
│ current_count    │ INTEGER           │ default 0                      │
│ best_count       │ INTEGER           │ default 0                      │
│ last_active_date │ DATE              │ nullable                       │
│ created_at       │ TIMESTAMPTZ       │ server default                 │
│ updated_at       │ TIMESTAMPTZ       │ onupdate                       │
└──────────────────┴───────────────────┴────────────────────────────────┘
```

**Unique constraint:** `(user_id, type)` — har user uchun har streak type faqat 1 ta.

**Tayyor belgisi:** Migration yaratiladi, jadval DB da paydo bo'ladi.

---

### Qadam 2: Streak service — core logic
**backend/app/services/streak_service.py:**

```python
STREAK_MILESTONES = {3: 0, 7: 25, 14: 50, 30: 100, 60: 200, 90: 300, 180: 500, 365: 1000}

async def get_or_create_streak(db, user_id, streak_type) -> Streak:
    """Streak topish yoki yaratish."""

async def update_streak(db, user_id, streak_type) -> dict:
    """
    Streak'ni bugungi sana uchun yangilash.
    Logic:
    1. Streak topish/yaratish
    2. last_active_date == today → hech narsa qilmaslik (allaqachon yangilangan)
    3. last_active_date == yesterday → current_count += 1 (davom)
    4. last_active_date < yesterday → current_count = 1 (qayta boshlash)
    5. best_count yangilash (agar current > best)
    6. Milestone check → coins reward
    Returns: {current_count, best_count, is_milestone, milestone_coins}
    """

async def get_user_streaks(db, user_id) -> list[Streak]:
    """Barcha user streak'larini olish."""

async def check_milestone(current_count) -> tuple[bool, int]:
    """Milestone tekshirish. Returns (is_milestone, coins_reward)."""
```

**Muhim:** Streak update **idempotent** — bir kunda bir necha marta chaqirilsa ham faqat 1 marta yangilanadi (`last_active_date == today` check).

---

### Qadam 3: Activity streak integration — task/habit complete'da
**Qayerga qo'shiladi:**

1. **Task complete** (`POST /api/tasks/{id}/complete`):
   - Task complete bo'lgandan keyin → `update_streak(db, user_id, "activity")`

2. **Habit log** (`POST /api/habits/{id}/log`):
   - Habit log yaratilganda (is_new=True, completed=True) → `update_streak(db, user_id, "activity")`
   - Shuningdek → `update_streak(db, user_id, f"habit_{habit_id}")` (per-habit streak)

**Keyinroq (Task 10):** Focus session complete → activity streak update

**Tayyor belgisi:** Task complete yoki habit log bo'lganda activity streak avtomatik yangilanadi.

---

### Qadam 4: Milestone reward integration
**Milestone'da nima bo'ladi:**
1. `update_streak()` milestone detect qiladi
2. Coins `user_progress.coins_balance` ga qo'shiladi
3. Response'da `is_milestone: true, milestone_coins: X` qaytadi

**Streak endpoint response'da milestone info ko'rsatiladi:**
- Task complete response'ga streak info qo'shish
- Habit log response'ga streak info qo'shish

---

### Qadam 5: API endpoint — GET /api/streaks
**backend/app/api/routes/streaks.py:**

```python
GET /api/streaks → list[StreakResponse]
# Response:
# [
#   {"type": "activity", "current_count": 5, "best_count": 12, "last_active_date": "2026-03-15"},
#   {"type": "habit_cbb114aa-...", "current_count": 3, "best_count": 3, ...},
#   ...
# ]
```

**Pydantic schema:**
```python
class StreakResponse(BaseModel):
    type: str
    current_count: int
    best_count: int
    last_active_date: date | None
```

**Tayyor belgisi:** Endpoint ishlaydi, barcha streak'lar ko'rinadi.

---

### Qadam 6: main.py yangilash + models update

- `models/__init__.py` ga `Streak` qo'shish
- `main.py` ga streaks router include
- Task complete va habit log endpoint'lariga streak update qo'shish

---

### Qadam 7: Verification

1. Task complete → activity streak = 1
2. Habit log → activity streak hali 1 (bir kunda faqat 1 marta oshadi)
3. Habit log → habit streak = 1
4. `GET /api/streaks` → activity va habit streak ko'rinadi
5. Milestone test: streak 7 ga yetganda +25 coins berilganini tekshirish
6. DB da `streaks` jadvalida to'g'ri ma'lumot borligini tekshirish

**Agar hamma narsa ishlasa — Task 9 yakunlangan. ✅**

---

## Eslatmalar

- **Streak freeze** — Task 23 da (Coin economy) implement qilinadi
- **Focus streak** — Task 10 da (Focus engine) qo'shiladi
- **Planning streak** — Task 12 da (Reminder engine) qo'shiladi
- **Streak break notification** — Task 12 da (Reminder engine) bot xabari sifatida
- **Streak share card** — Task 29 da (Shareable cards)
- Hozircha faqat **activity** va **habit** streak ishga tushiriladi
