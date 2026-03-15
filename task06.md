# Task 6: Task Completion Logic va XP Award

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 8 qadam
**Dependency:** Task 5 ✅
**Output:** `POST /api/tasks/{id}/complete` ishlaydi. XP hisoblanadi (base + multipliers), `xp_events` ga yoziladi, `user_progress` yangilanadi, level-up detection ishlaydi. Daily cap 500 XP.

---

## Qadamlar

### Qadam 1: xp_events va user_progress model + migration
**2 ta yangi jadval:**

```
xp_events:
  id, user_id (FK), source_type (task/habit/focus/mission/...),
  source_id (UUID), xp_amount (INT), created_at

user_progress:
  id, user_id (FK, UNIQUE), total_xp (INT, default 0),
  current_level (INT, default 1), coins_balance (INT, default 0),
  created_at, updated_at
```

**Tayyor belgisi:** `alembic upgrade head` → 2 jadval yaratiladi.

---

### Qadam 2: XP calculation logic
**backend/app/services/xp_service.py:**

- `DIFFICULTY_XP_MAP`: trivial=5, easy=10, medium=20, hard=35, epic=50
- `calculate_task_xp(task)` → base × multipliers
  - same-day: planned_date == today → ×1.2
  - critical priority → ×1.5
  - goal-linked → ×1.15 (task.goal_id not null)
- `get_daily_xp_total(db, user_id, date)` → bugungi jami XP
- Daily cap: 500 XP (cap ga yetsa, qolgan qismi berilmaydi)

---

### Qadam 3: Level system logic
- Level formula: `required_xp(level) = floor(50 × level^1.8)`
- `get_level_for_xp(total_xp)` → current level
- `get_xp_for_next_level(current_level)` → keyingi level uchun kerak XP
- `check_level_up(old_xp, new_xp)` → (old_level, new_level, leveled_up)
- Level-up reward: coins = level × 10

---

### Qadam 4: Award XP service function
**`award_xp(db, user_id, source_type, source_id, xp_amount)`:**
1. Daily cap tekshirish
2. `xp_events` ga insert
3. `user_progress.total_xp` yangilash
4. Level-up check → coins berish
5. Return: (xp_awarded, new_total, leveled_up, new_level)

---

### Qadam 5: Task complete endpoint
**`POST /api/tasks/{id}/complete`:**
1. Task topish (user_id check)
2. Status "pending" ekanini tekshirish
3. XP hisoblash → `calculate_task_xp(task)`
4. XP berish → `award_xp()`
5. Task yangilash: status=completed, completed_at=now(), xp_awarded=amount
6. Return: TaskCompleteResponse (task + xp_awarded + leveled_up info)

---

### Qadam 6: Progress endpoint
**`GET /api/users/me/progress`:**
- current_level, total_xp, xp_for_current_level, xp_for_next_level
- coins_balance
- Progress percentage to next level

---

### Qadam 7: Models/main.py yangilash + user_progress auto-create
- Models `__init__` ga XpEvent, UserProgress qo'shish
- User yaratilganda `user_progress` ham yaratish (user_service.py yangilash)

---

### Qadam 8: Verification
1. Task complete → XP beriladi, xp_events ga yoziladi
2. `GET /api/users/me/progress` → level, xp, coins ko'rinadi
3. Ko'p task complete → daily cap 500 XP da to'xtaydi
4. Level-up bo'lganda coins beriladi
5. Allaqachon completed task → xato (qayta complete bo'lmasligi kerak)
