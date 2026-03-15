# PlanQuest — Development Task Breakdown

**Jami: 32 task**
**Tartib: har bir task oldingi task(lar)ga dependency bo'yicha ketma-ket tartiblangan**
**Har bir task mustaqil commit/PR sifatida yakunlanishi kerak**

---

## PHASE 0 — Project Setup & Infrastructure

### Task 1: Project initialization va monorepo structure
**Scope:** Loyiha skeletini yaratish
- `/backend` — Python FastAPI project (`pyproject.toml`, `uv` yoki `poetry`)
- `/frontend` — Next.js + React + TypeScript + Tailwind project
- `/docker` — Docker Compose (postgres, redis, backend, frontend)
- `.env.example` fayl
- `Makefile` yoki `justfile` (dev commands: `make up`, `make migrate`, `make test`)
- `.gitignore`, `README.md`

**Output:** `docker compose up` bilan backend + frontend + postgres + redis ishga tushadi, health check endpoint `/health` javob beradi.

---

### Task 2: Database schema va migration system
**Scope:** Alembic migration setup + core jadvallar
- Alembic konfiguratsiyasi
- Core jadvallar migration:
  - `users` (telegram_id, first_name, username, segment, timezone, language, created_at, updated_at)
  - `user_settings` (user_id FK, morning_reminder_time, evening_reminder_time, quiet_hours_start, quiet_hours_end, theme)
- SQLAlchemy model'lar (`models/user.py`)
- Database connection pool (asyncpg)

**Output:** `alembic upgrade head` users va user_settings jadvallarini yaratadi.

**Dependency:** Task 1

---

### Task 3: Telegram Bot foundation — webhook va command handler
**Scope:** Bot skeleti — webhook qabul qilish va asosiy komandalarni handle qilish
- Telegram Bot API webhook setup (`/api/telegram/webhook`)
- `python-telegram-bot` yoki `aiogram` integration
- `/start` command handler (faqat "Salom" javob beradi)
- `/help` command handler
- Webhook registration script
- Bot token `.env` orqali
- Request validation (Telegram webhook signature check)

**Output:** Bot `/start` va `/help` komandalarga javob beradi. Webhook ishlaydi.

**Dependency:** Task 1

---

### Task 4: Auth system — Telegram initData verification
**Scope:** Telegram Mini App va Bot dan kelgan user'ni authenticate qilish
- Telegram initData HMAC-SHA256 verification middleware
- Bot update'dan user extraction va auto-registration
- Mini App auth endpoint: `POST /api/auth/telegram` (initData → JWT token)
- JWT token generation va verification
- Auth middleware (protected routes uchun)
- User auto-create: yangi Telegram user kelsa, `users` jadvaliga insert

**Output:** Bot orqali kelgan user auto-register bo'ladi. Mini App initData yuborsa JWT oladi. Protected endpoint'lar ishlaydi.

**Dependency:** Task 2, Task 3

---

## PHASE 1 — Core Productivity Features

### Task 5: Task engine — CRUD API
**Scope:** Task yaratish, o'qish, yangilash, o'chirish
- Database migration: `tasks` jadvali (id, user_id, title, notes, planned_date, due_date, priority, difficulty, estimated_minutes, category, status, recurrence_rule, created_at, completed_at, source)
- SQLAlchemy model: `Task`
- Pydantic schemas: `TaskCreate`, `TaskUpdate`, `TaskResponse`
- API endpoints:
  - `POST /api/tasks` — yaratish
  - `GET /api/tasks?date=2026-03-16&status=pending` — filterlash
  - `GET /api/tasks/{id}` — bitta task
  - `PATCH /api/tasks/{id}` — yangilash
  - `DELETE /api/tasks/{id}` — o'chirish (soft delete → archive)
- Validation: title min 3 char, planned_date >= today, priority enum, difficulty enum

**Output:** API orqali task CRUD ishlaydi. Unit testlar yozilgan.

**Dependency:** Task 4

---

### Task 6: Task completion logic va XP award
**Scope:** Taskni "completed" qilish va XP hisoblash
- `POST /api/tasks/{id}/complete` endpoint
- XP calculation logic:
  - Base XP: trivial=5, easy=10, medium=20, hard=35, epic=50
  - Multiplier'lar: same-day ×1.2, critical ×1.5, goal-linked ×1.15
  - Daily cap: 500 XP
- Database migration: `xp_events` jadvali (id, user_id, source_type, source_id, xp_amount, created_at)
- XP event yaratish task complete bo'lganda
- Task status → completed, completed_at timestamp

**Output:** Task complete bo'lganda XP event yaratiladi. Daily cap ishlaydi.

**Dependency:** Task 5

---

### Task 7: Level system
**Scope:** XP asosida level hisoblash va level-up detection
- Database migration: `user_progress` jadvali (user_id, total_xp, current_level, coins_balance)
- Level formula: `required_xp(level) = floor(50 × level^1.8)`
- XP event yaratilganda → total_xp yangilash → level check
- Level-up detection: agar yangi total_xp keyingi level thresholdni o'tsa → level-up event
- Level-up reward: coins = level × 10
- API: `GET /api/users/me/progress` — current level, xp, next level xp, coins

**Output:** User XP to'plaganda level ko'tariladi, coins beriladi.

**Dependency:** Task 6

---

### Task 8: Habit engine — CRUD va daily logging
**Scope:** Habit yaratish va har kunlik log qilish
- Database migration:
  - `habits` jadvali (id, user_id, title, type, target_value, frequency, frequency_days, reminder_time, icon, color, status, created_at)
  - `habit_logs` jadvali (id, habit_id, user_id, date, value, completed, logged_at, source)
- SQLAlchemy model'lar
- API endpoints:
  - `POST /api/habits` — yaratish
  - `GET /api/habits` — user habitlari
  - `PATCH /api/habits/{id}` — yangilash
  - `DELETE /api/habits/{id}` — archive
  - `POST /api/habits/{id}/log` — bugungi log (value + date)
  - `GET /api/habits/{id}/logs?from=&to=` — log tarixi
- Habit types: yes_no, count, duration, avoid
- Completion rule: value >= target_value
- Habit log XP: yes_no=5, count=8, duration=10, avoid=7

**Output:** Habit CRUD va daily logging ishlaydi. XP beriladi.

**Dependency:** Task 7

---

### Task 9: Streak system
**Scope:** Activity streak va habit streak hisoblash
- Database migration: `streaks` jadvali (id, user_id, type, current_count, best_count, last_active_date, updated_at)
- Streak types: `activity`, `habit_{id}`, `focus`, `planning`
- Activity streak logic:
  - Har kuni kamida 1 meaningful action (task complete / habit log / focus complete)
  - Midnight (user timezone) da check
  - Agar bugun action bo'lsa → streak +1
  - Agar bugun action bo'lmasa → streak = 0 (yoki freeze ishlatilsa saqlanadi)
- Habit streak: habit_logs chain asosida hisoblash
- Streak milestone detection: 3, 7, 14, 30, 60, 90, 180, 365
- Streak milestone rewards: coins (PRD bo'yicha)
- API: `GET /api/streaks` — barcha user streaklari

**Output:** Task/habit complete bo'lganda streak yangilanadi. Milestone'larda reward beriladi.

**Dependency:** Task 8

---

### Task 10: Focus session engine
**Scope:** Pomodoro / deep work timer backend
- Database migration: `focus_sessions` jadvali (id, user_id, task_id, planned_duration, actual_duration, mode, status, started_at, ended_at, xp_awarded)
- API endpoints:
  - `POST /api/focus/start` — session boshlash (duration, mode, task_id optional)
  - `POST /api/focus/{id}/end` — session tugatish
  - `GET /api/focus/active` — joriy aktiv session
  - `GET /api/focus/history?from=&to=` — tarix
  - `GET /api/focus/stats` — daily/weekly totals
- XP: pomodoro_25=15, deep_50=30, ultra_90=50
- Minimum 50% duration → XP beriladi
- Daily focus XP cap: 200
- Focus streak update

**Output:** Focus session boshlash/tugatish ishlaydi. XP va streak yangilanadi.

**Dependency:** Task 9

---

### Task 11: Bot command handlers — task va habit operations
**Scope:** Bot orqali task va habit bilan ishlash
- `/add [title] [date]` — task yaratish (date parsing: "bugun", "ertaga", "2026-03-20")
- `/today` — bugungi tasklar ro'yxati inline button'lar bilan (✅ Done, ⏰ Tomorrow)
- `/habits` — bugungi habitlar inline button'lar bilan (✅ Done, ⏭ Skip)
- `/focus [minutes]` — focus session boshlash
- `/stats` — level, XP, streak, bugungi score
- Callback query handler: inline button bosilganda task complete / habit log / reschedule
- Callback response: original message edit qilish (yangi status ko'rsatish)

**Output:** Bot orqali task/habit/focus/stats bilan ishlash mumkin.

**Dependency:** Task 10

---

### Task 12: Reminder engine (scheduled notifications)
**Scope:** Vaqtga asoslangan bot xabarlari
- Celery + Redis setup (yoki APScheduler / arq)
- Celery beat scheduler (periodic tasks)
- Reminder types implementation:
  - Morning plan: user'ning morning_reminder_time da bugungi plan
  - Evening summary: user'ning evening time da kunlik xulosa
  - Streak warning: 20:00 da agar bugun action yo'q bo'lsa
- Timezone-aware scheduling (user timezone bo'yicha)
- Anti-spam: max 6 message/day, quiet hours check
- Morning message template: bugungi tasklar, habitlar, streak status
- Evening message template: completed count, XP earned, streak status

**Output:** Bot avtomatik ravishda morning/evening/streak xabarlarni yuboradi.

**Dependency:** Task 11

---

### Task 13: Onboarding flow
**Scope:** Yangi user uchun bot onboarding
- `/start` handler yangilash:
  1. Welcome message + segment selection (inline buttons: Student, Freelancer, Entrepreneur, Developer, Other)
  2. Segment callback → user.segment saqlash
  3. "Birinchi taskingni yoz" prompt
  4. User text → task yaratish → "+10 XP!" response
  5. Reminder vaqti tanlash (inline buttons: 7:00, 8:00, 9:00, 10:00)
  6. Setup complete message + Mini App deep link
- Deep link handling: `?start=ref_CODE` → referral tracking
- Onboarding state tracking (user qaysi bosqichda ekanini bilish)

**Output:** Yangi user 3 bosqichli onboarding'dan o'tadi, segment va reminder time saqlanadi.

**Dependency:** Task 12

---

## PHASE 2 — Mini App Frontend

### Task 14: Mini App shell — routing, auth, layout
**Scope:** Mini App frontend skeleti
- Next.js app setup (Telegram Mini Apps SDK integration)
- `@telegram-apps/sdk-react` integration
- Auth flow: initData → backend JWT → axios/fetch interceptor
- Layout: bottom navigation (Home, Planner, Habits, Progress, Profile)
- Telegram theme integration (dark/light mode)
- Responsive design (mobile-first, Telegram WebApp viewport)
- Loading states, error boundaries
- API client service (`/lib/api.ts`)

**Output:** Mini App Telegram ichida ochiladi, auth ishlaydi, 5 ta tab navigatsiya ishlaydi.

**Dependency:** Task 4

---

### Task 15: Home screen
**Scope:** Mini App bosh sahifasi
- Greeting (user ismi + vaqtga qarab: "Xayrli tong", "Xayrli kun")
- Today's score: completed / planned tasks ratio (progress ring)
- Top 3 priority tasks (checkbox bilan complete qilish mumkin)
- Today's habits (quick log buttons)
- Current streak display (flame icon + raqam)
- Daily mission progress (3 ta mission card — Task 21 dan keyin to'liq ishlaydi, hozir placeholder)
- Focus CTA button ("Start Focus Session")

**Output:** Home screen barcha bugungi ma'lumotlarni ko'rsatadi, task complete va habit log qilish mumkin.

**Dependency:** Task 14

---

### Task 16: Planner screen
**Scope:** Task management UI
- Calendar date selector (horizontal scrollable week view)
- Daily / Weekly tab toggle
- Task list: title, priority badge, difficulty badge, estimated time
- Task completion: checkbox tap → API call → XP animation
- Add task: FAB button → bottom sheet form (title, date, priority, difficulty, estimate)
- Task detail: tap → full detail modal (edit, reschedule, delete, start focus)
- Carry-forward tray: overdue tasks section (highlighted)
- Empty state: "No tasks for today. Add one!"

**Output:** Planner'da task ko'rish, yaratish, complete qilish, edit qilish ishlaydi.

**Dependency:** Task 15

---

### Task 17: Habits screen
**Scope:** Habit management UI
- Today's habits list (cards with streak count, type icon)
- One-tap logging: yes/no → tap, count → number input, duration → minutes input
- Log animation: checkmark + XP pill
- Habit detail screen: heatmap (GitHub-style), streak history, consistency %, edit
- Add habit: bottom sheet (title, type, target, frequency, reminder time, icon, color)
- Habit templates: popular pre-configured habits (Read, Exercise, Meditate, Journal, Water)

**Output:** Habit'larni ko'rish, log qilish, yaratish, detail ko'rish ishlaydi.

**Dependency:** Task 15

---

### Task 18: Progress screen
**Scope:** Analytics va progression UI
- XP bar (current XP / next level XP, animated)
- Level display (raqam + title)
- Streak cards (activity, focus, planning — flame icon + count)
- Weekly completion chart (bar chart — last 7 days)
- Achievement section (placeholder — Task 22 da to'liq bo'ladi)
- Stats cards: total tasks completed, total focus minutes, total habits logged, best streak

**Output:** Progress screen level, XP, streak, weekly chart ko'rsatadi.

**Dependency:** Task 15

---

### Task 19: Profile screen
**Scope:** User profili va sozlamalar
- User info: Telegram avatar, username, current title, level badge
- Coins balance display
- Streak freeze token count
- Settings:
  - Timezone (auto-detect + manual override)
  - Morning reminder time
  - Evening reminder time
  - Quiet hours
  - Theme toggle (light/dark/system)
  - Language (keyingi bosqich uchun placeholder)
- Premium status (placeholder — Task 28 da to'liq)
- Data export button (placeholder)

**Output:** Profile va settings ishlaydi, sozlamalar backend'ga saqlanadi.

**Dependency:** Task 15

---

### Task 20: Focus timer screen
**Scope:** Focus session UI
- Mode selector: 25 min, 50 min, 90 min, Custom
- Task linker: "Link to task" dropdown (bugungi tasklar ro'yxati)
- Timer display: katta countdown raqam, progress ring
- Controls: Start, Pause, End
- Session active state: minimal UI (faqat timer va pause)
- Session complete: celebration animation, XP popup, summary card
- Summary: duration, XP earned, linked task status
- Break timer option: 5 min / 15 min
- Daily focus stats: total minutes today

**Output:** Focus timer to'liq ishlaydi — boshlash, pause, tugatish, XP olish.

**Dependency:** Task 15, Task 10

---

## PHASE 3 — Gamification Engine

### Task 21: Mission system
**Scope:** Daily va weekly mission'lar
- Database migration:
  - `missions` jadvali (id, user_id, type, title, description, target_value, current_value, reward_xp, reward_coins, status, date/week, created_at)
- Daily mission generation (Celery cron — midnight user timezone):
  - Mission 1: easy (complete 1 task)
  - Mission 2: behavior-shaping (use underused feature)
  - Mission 3: stretch (user average + 1)
- Weekly mission generation (Monday):
  - 4 ta haftalik mission
- Mission progress tracking: har bir relevant event da mission progress check
- Mission completion → XP + coins award
- API: `GET /api/missions?type=daily&date=today`, `GET /api/missions?type=weekly`
- Mini App: Home screen'dagi mission card'larni to'liq qilish
- Bot: `/missions` command

**Output:** Har kuni 3 mission, har hafta 4 mission avtomatik yaratiladi va progress tracking ishlaydi.

**Dependency:** Task 12, Task 15

---

### Task 22: Achievement system
**Scope:** Achievement catalog va event-driven tracking
- Database migration:
  - `achievements` jadvali (id, key, name, description, category, requirement_type, requirement_value, reward_xp, reward_coins, icon)
  - `user_achievements` jadvali (id, user_id, achievement_id, progress, unlocked, unlocked_at)
- Achievement catalog seed data (PRD bo'yicha ~25 ta achievement)
- Event-driven progress tracking:
  - task.completed → "Task Centurion" progress +1
  - streak milestone → "7-Day Warrior" unlock
  - focus.completed → "Deep Worker" progress +minutes
- Achievement unlock → bot notification + XP/coins award
- API: `GET /api/achievements` — barcha achievements + user progress
- Mini App: Progress screen achievement gallery (locked/unlocked, progress bars)

**Output:** Achievement'lar avtomatik track qilinadi, unlock bo'lganda reward va notification beriladi.

**Dependency:** Task 21

---

### Task 23: Coin economy va streak freeze
**Scope:** Coin earning/spending system
- Coin earning implementation (level-up, missions, achievements, streak milestones — barchasi avval qilingan event'larga coins qo'shish)
- Database migration: `wallet_transactions` jadvali (id, user_id, amount, type, source, description, created_at)
- Streak freeze mechanic:
  - `POST /api/shop/streak-freeze` — 50 coins sarflab 1 freeze token olish
  - `rewards_inventory` jadvali (user_id, item_type, quantity)
  - Streak engine'da freeze check: agar streak sinishi kerak va freeze token bor → token ishlatish, streak saqlash
- API: `GET /api/wallet` — balance + transaction history
- Mini App: Profile screen coins display, freeze token count

**Output:** Coins to'planadi, streak freeze sotib olish va ishlatish ishlaydi.

**Dependency:** Task 22

---

### Task 24: Reward chests
**Scope:** Chest generation va loot system
- Database migration:
  - `chests` jadvali (id, user_id, type, status, loot_data, created_at, opened_at)
- Chest types: daily (3/3 mission), weekly (4/4 mission), streak (milestones), level (har 5 level)
- Chest generation triggers:
  - All daily missions complete → daily chest
  - All weekly missions complete → weekly chest
  - Streak milestone → streak chest
  - Level 5, 10, 15, 20... → level chest
- Loot table: random coins (range by type), cosmetic chance %, freeze token chance %
- `POST /api/chests/{id}/open` — chest ochish, loot berish
- API: `GET /api/chests` — unopened chests
- Mini App: chest notification badge, open animation (simple)

**Output:** Mission/streak/level milestone'larda chest paydo bo'ladi, ochganda loot oladi.

**Dependency:** Task 23

---

## PHASE 4 — AI Planning System (Premium Only)

**Arxitektura:** Orchestrator + Specialized Agents (ai-architecture.md ga qarang)
**Access:** Faqat Premium foydalanuvchilar. Free user'larga "Premium kerak" ko'rsatiladi.

### Task 25: AI foundation — module structure, provider, logging
**Scope:** AI infratuzilma — arxitektura skelet, Claude provider, request logging, rate limiter
- `app/ai/` module structure yaratish (ai-architecture.md Section 13 bo'yicha):
  - `orchestrator/` — router.py, orchestrator.py, rate_limiter.py
  - `agents/` — base.py (BaseAgent abstract class)
  - `prompts/` — bo'sh modul (keyingi task'larda to'ldiriladi)
  - `tools/` — context.py (UserContext builder)
  - `schemas/` — context.py (UserContext Pydantic model)
  - `validators/` — schema_validator.py, sanitizer.py
  - `providers/` — base.py (BaseProvider), claude.py (Anthropic SDK wrapper)
  - `services/` — ai_service.py (high-level entry point)
  - `mappers/` — bo'sh modul
- `anthropic` Python SDK dependency qo'shish
- Claude provider:
  - `call(system_prompt, user_message, model, max_tokens)` → JSON string
  - Retry logic: 1 retry on timeout/5xx, 2s backoff
  - Response JSON parse + schema validation
  - Token count tracking
- `ai_request_logs` DB model + migration:
  - id, user_id, agent, model, input_tokens, output_tokens, latency_ms, status, cached, retry_count, created_at
- Redis rate limiter:
  - Key: `ai:rate:{user_id}:{date}`, max 30 calls/day
  - Premium check middleware for `/api/ai/*` routes
- Redis cache layer:
  - `get_cached(key)`, `set_cached(key, data, ttl)`
- Config: `AI_MODEL_DEFAULT`, `AI_MODEL_ADVANCED`, `ANTHROPIC_API_KEY` settings
- Health check: AI provider connectivity test

**Output:** AI module skeleti tayyor. Claude API ishlaydi. Logging, rate limit, cache bor.

**Dependency:** Task 4, Task 23

---

### Task 26: Planner Agent — daily plan generation
**Scope:** Birinchi agent — kunlik reja yaratish (ai-architecture.md Section 4, Agent 1)
- `agents/planner.py` — PlannerAgent class
- `prompts/planner.py` — system prompt (structured JSON output, safety rules)
- `schemas/plans.py` — DailyPlan, TimeBlock, SuggestedTask Pydantic models
- `validators/plan_validator.py`:
  - Max 15 tasks/day
  - Max 10 soat scheduled
  - Time blocks 06:00-23:00
  - Task/habit ID existence check
  - No overlapping time blocks
  - Workload realism check
- `tools/tasks.py` — get_active_tasks, get_overdue_tasks (read-only)
- `tools/habits.py` — get_active_habits (read-only)
- `tools/analytics.py` — get_basic_stats (avg tasks/day, focus minutes)
- `tools/context.py` — PlannerContext builder (minimal token usage)
- `mappers/plan_mapper.py` — DailyPlan → list[TaskCreate] conversion
- API endpoints:
  - `POST /api/ai/plan` — reja yaratish (preview qaytaradi)
  - `POST /api/ai/plan/apply` — user tasdiqlagan rejani qo'llash
- Cache: `ai:plan:{user_id}:{date}` key, 4 soat TTL, task change'da invalidate
- Bot: `/plan` command → plan preview → [Qo'llash] [Bekor] inline buttons
- Mini App: AI Planner screen — request → preview cards → approve/edit

**Output:** User `/plan` yoki Mini App'dan AI reja so'raydi → preview ko'radi → tasdiqlaydi → tasklar yaratiladi.

**Dependency:** Task 25

---

### Task 27: Goal system + Goal Breakdown Agent
**Scope:** Goal CRUD + AI decomposition (ai-architecture.md Section 4, Agent 2)
- Database migration:
  - `goals` jadvali (id, user_id, parent_goal_id, title, description, category, level, target_date, progress_percent, status, created_at)
- Goal API endpoints:
  - `POST /api/goals` — yaratish
  - `GET /api/goals` — user goals (tree structure)
  - `PATCH /api/goals/{id}` — yangilash
  - `DELETE /api/goals/{id}` — archive
- Goal hierarchy: yearly → monthly → weekly
- Progress calculation: linked tasks completed / total linked tasks
- Task-goal linking: task yaratishda goal_id field
- `agents/goal_breakdown.py` — GoalBreakdownAgent
- `prompts/goal_breakdown.py` — system prompt
- `schemas/goals.py` — GoalDecomposition, Milestone Pydantic models
- `validators/business_rules.py` — milestone count limits, task count per milestone
- `mappers/goal_mapper.py` — Milestones → TaskCreate objects
- API: `POST /api/ai/goals/{id}/decompose` — AI decomposition → preview → apply
- Mini App: Goals screen (list, progress bars, "AI bilan bo'lish" button)
- Bot: `/goals` command

**Output:** Goal CRUD ishlaydi. AI goal decomposition preview + apply ishlaydi.

**Dependency:** Task 26

---

### Task 27.5: Recovery Agent + Coaching Agent
**Scope:** Qaytish rejasi + coaching insights (ai-architecture.md Section 4, Agent 3 va 4)
- `agents/recovery.py` — RecoveryAgent
- `prompts/recovery.py` — system prompt
- `schemas/recovery.py` — RecoveryPlan Pydantic model
- Recovery detection: user 1+ kun inactive → auto-trigger recovery suggestion
- API: `POST /api/ai/recover` — recovery plan preview
- Bot: `/recover` command
- Mini App: user qaytganda "Qaytish rejasi" banner ko'rinadi
- `agents/coaching.py` — CoachingAgent
- `prompts/coaching.py` — system prompt
- `schemas/coaching.py` — CoachingInsights Pydantic model
- `tools/analytics.py` (kengaytirish) — 14 kunlik pattern analysis
- Burnout detection: declining completion + reduced focus → warning
- API: `GET /api/ai/coach` — coaching insights
- Bot: `/coach` command
- Mini App: Progress screen'da "AI Coaching" tab
- Celery: haftalik coaching summary (Sunday)
- Model routing: Coaching = claude-sonnet, Recovery = claude-haiku

**Output:** Recovery plan qaytish uchun, Coaching insights pattern analysis bilan ishlaydi.

**Dependency:** Task 27

---

### Task 27.6: Mission Design Agent + Motivation Copy Agent
**Scope:** Personalized missions + motivational text (ai-architecture.md Section 4, Agent 5 va 6)
- `agents/mission_design.py` — MissionDesignAgent
- `prompts/mission_design.py` — system prompt
- `schemas/missions.py` — MissionSuggestions Pydantic model
- Premium user'lar uchun Celery daily mission generation'da random template o'rniga AI agent ishlatish
- Mission reward bounds: XP 10-100, Coins 5-50
- `validators/business_rules.py` — reward bounds check
- `agents/motivation.py` — MotivationCopyAgent
- `prompts/motivation.py` — system prompt
- `schemas/motivation.py` — MotivationCopy Pydantic model
- Premium user reminder'larida AI-generated personalized matn
- Max 280 chars, tone control, CTA support
- Celery integration: morning/evening reminder text generation
- Batch optimization: bir API call'da 5 ta user uchun motivation generate
- Fallback: AI ishlamasa eski template'lar ishlatiladi

**Output:** Premium user'lar uchun personalized mission'lar va motivational notification'lar.

**Dependency:** Task 27.5

---

## PHASE 5 — Social & Viral Features

### Task 28: Referral system
**Scope:** Invite link va reward tracking
- Database migration:
  - `referrals` jadvali (id, referrer_user_id, referred_user_id, referral_code, status, created_at, activated_at)
- Unique referral code generation (user_id hash based, 8 char)
- Deep link: `t.me/PlanQuestBot?start=ref_CODE`
- `/start ref_CODE` handling: referral record yaratish
- Referral activation: referred user onboarding complete → referrer +100 XP, +50 coins; referred +50 coins
- D7 bonus: referred user 7 kun active → referrer +50 XP, +25 coins
- Anti-abuse: max 50 referrals, unique telegram_id, self-referral block
- API: `GET /api/referrals` — user referral stats
- Bot: `/invite` — referral link va stats

**Output:** Referral link ishlaydi, reward beriladi, abuse prevention ishlaydi.

**Dependency:** Task 23

---

### Task 29: Shareable progress cards
**Scope:** Image card generation va sharing
- Server-side PNG generation (Pillow yoki html2image)
- Card templates:
  - Streak card: avatar, streak count, flame graphic
  - Level-up card: level badge, title, total XP
  - Weekly win card: tasks done, habits logged, focus minutes
- API: `GET /api/cards/streak`, `GET /api/cards/level`, `GET /api/cards/weekly` → PNG image response
- Bot: streak/level milestone xabarlariga "[Share]" button → card image + forward prompt
- Deep link embedded in card (QR code yoki text link)
- Card caching: 24 soat cache

**Output:** Milestone'larda chiroyli card image yaratiladi, share qilish mumkin.

**Dependency:** Task 28

---

### Task 30: Weekly review system
**Scope:** Haftalik ko'rib chiqish flow
- Weekly stats aggregation:
  - Tasks: created, completed, rescheduled, overdue
  - Habits: consistency per habit, best/worst
  - Focus: total minutes, sessions count
  - XP earned, level change
  - Streak status
  - Goal progress delta
- `GET /api/reviews/weekly?week=2026-W12` — weekly stats
- Weekly review completion tracking (user opened and scrolled through)
- Weekly review XP: +30 XP
- Bot: Sunday 18:00 reminder → "Haftalik ko'rib chiqish tayyor" + [Open Review] button
- Mini App: dedicated weekly review screen (stats cards, charts, AI insight placeholder)

**Output:** Haftalik review stats to'planadi, Mini App'da ko'rinadi, XP beriladi.

**Dependency:** Task 18

---

## PHASE 6 — Production Readiness

### Task 31: Event system va cross-module integration
**Scope:** Domain event bus va barcha module'larni birlashtirish
- Internal event bus (Python signals yoki simple pub/sub)
- Domain events:
  - `task.completed` → XP, streak, mission progress, achievement progress, analytics
  - `habit.logged` → XP, streak, mission, achievement, analytics
  - `focus.completed` → XP, streak, mission, achievement, analytics
  - `mission.completed` → chest generation, XP, coins
  - `achievement.unlocked` → coins, bot notification
  - `level.up` → coins, chest, bot notification
  - `streak.milestone` → coins, chest, bot notification, card generation
- Idempotency: har bir event faqat 1 marta process bo'lishi
- Event log table: `domain_events` (id, type, payload, processed, created_at)
- Barcha modul'larni event orqali bog'lash (direct call o'rniga)

**Output:** Barcha module'lar event bus orqali muvofiqlashtirilgan. Bitta action ko'p oqibatni trigger qiladi.

**Dependency:** Task 24, Task 22

---

### Task 32: Testing, error handling va deploy tayyorlash
**Scope:** Production uchun tayyorgarlik
- Backend unit testlar (pytest):
  - Auth tests
  - Task CRUD tests
  - XP calculation tests
  - Streak logic tests
  - Mission generation tests
- Integration testlar:
  - Bot webhook → task create → XP → level flow
  - Focus session → complete → streak update flow
- Error handling:
  - Global exception handler
  - Sentry integration
  - Structured logging (JSON logs)
- Rate limiting: per-user API limits (100 req/min)
- Health checks: `/health` (DB, Redis, Celery connectivity)
- Docker production config:
  - Multi-stage Dockerfile (backend)
  - Nginx config (frontend)
  - Docker Compose production override
- CI/CD pipeline (GitHub Actions):
  - Lint (ruff/eslint)
  - Test
  - Build
  - Deploy (docker compose up on server)
- `.env.production.example`

**Output:** Testlar yashil, error tracking ishlaydi, production deploy tayyor.

**Dependency:** Task 31

---

## Task Dependency Graph (qisqacha)

```
Task 1 (project init)
├── Task 2 (database) ──┐
├── Task 3 (bot)────────├── Task 4 (auth)
│                        │    ├── Task 5 (task CRUD)
│                        │    │    └── Task 6 (task XP)
│                        │    │         └── Task 7 (levels)
│                        │    │              └── Task 8 (habits)
│                        │    │                   └── Task 9 (streaks)
│                        │    │                        └── Task 10 (focus)
│                        │    │                             └── Task 11 (bot commands)
│                        │    │                                  └── Task 12 (reminders)
│                        │    │                                       └── Task 13 (onboarding)
│                        │    │
│                        │    └── Task 14 (mini app shell)
│                        │         └── Task 15 (home screen)
│                        │              ├── Task 16 (planner)
│                        │              ├── Task 17 (habits UI)
│                        │              ├── Task 18 (progress) ── Task 30 (weekly review)
│                        │              └── Task 19 (profile)
│                        │         └── Task 20 (focus UI)
│                        │
│                        │    Task 25 (AI service) ── Task 26 (AI planner) ── Task 27 (goals)
│                        │
│                        └── Task 21 (missions)
│                             └── Task 22 (achievements)
│                                  └── Task 23 (coins)
│                                       ├── Task 24 (chests)
│                                       └── Task 28 (referrals)
│                                            └── Task 29 (cards)
│
└── Task 31 (event system) ── Task 32 (testing & deploy)
```

---

## Parallel ishlash mumkin bo'lgan tasklar

Quyidagi tasklar **bir vaqtda** ishlanishi mumkin (agar 2+ developer bo'lsa):

| Backend developer | Frontend developer |
|---|---|
| Task 5–13 (backend features) | Task 14–20 (Mini App UI) |
| Task 21–24 (gamification backend) | Task 15–20 screen'larni polish qilish |
| Task 25–27 (AI system) | Task 30 (weekly review UI) |
| Task 28–29 (viral backend) | Task 29 (card UI integration) |
| Task 31–32 (integration & deploy) | Task 32 (frontend tests & build) |

---

## Estimated timeline

| Phase | Tasklar | Davomiyligi (1 backend + 1 frontend dev) |
|-------|---------|------------------------------------------|
| Phase 0 — Setup | Task 1–4 | 1.5 hafta |
| Phase 1 — Core Backend | Task 5–13 | 3–4 hafta |
| Phase 2 — Mini App | Task 14–20 | 3–4 hafta (parallel with Phase 1) |
| Phase 3 — Gamification | Task 21–24 | 2–3 hafta |
| Phase 4 — AI System | Task 25–27 | 2 hafta |
| Phase 5 — Social/Viral | Task 28–30 | 1.5 hafta |
| Phase 6 — Production | Task 31–32 | 1.5 hafta |
| **JAMI** | **32 task** | **~10–12 hafta** |

---

## Ishni boshlash tartibi

**1-kun:** Task 1 → project init, Docker, health check
**2–3-kun:** Task 2 + Task 3 → database + bot parallel
**4–5-kun:** Task 4 → auth system
**6-kun:** Task 5 + Task 14 → backend task CRUD + frontend shell (parallel boshlash)
**...davom etadi task tartibida...**

Har bir task yakunlanganda — commit, test, PR. Keyingi taskga o'tish.
