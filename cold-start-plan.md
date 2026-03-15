# Cold Start Plan — Yangi user uchun AI-ready onboarding

## Muammo

Yangi user kirganda:
- 0 task, 0 habit, 0 focus session, 0 streak
- AI planner chaqirilsa — bo'sh kontekst, yomon reja
- User nima qilishni bilmaydi — planner bo'sh, habits bo'sh
- Birinchi 3 kun ichida 70% user churn bo'ladi (cold start muammosi)

## Yechim — 3 qatlamli cold start

### Qatlam 1: Segment-based Starter Pack (onboarding tugaganda)

User segment tanlashi bilanoq (Student/Freelancer/Developer/Entrepreneur/Other), avtomatik yaratiladi:

**Starter Tasks (3-5 ta, bugunga):**

| Segment | Task 1 | Task 2 | Task 3 |
|---------|--------|--------|--------|
| Student | 📚 Darsga tayyorlanish (30m) | 📝 Konspekt yozish (20m) | 📖 Kitob o'qish (30m) |
| Freelancer | 📧 Email tekshirish (15m) | 💼 Bugungi loyiha ishi (60m) | 📋 Haftalik reja tuzish (15m) |
| Developer | 💻 Kod yozish (60m) | 📖 Documentation o'qish (30m) | 🐛 Bug fix qilish (30m) |
| Entrepreneur | 📊 KPI tekshirish (15m) | 🤝 Jamoa bilan meeting (30m) | 📈 Strategiya yozish (45m) |
| Other | ✅ Bugungi eng muhim ish (30m) | 📝 Kun rejasini yozish (10m) | 🏃 30 min harakatlanish (30m) |

**Starter Habits (2-3 ta):**

| Segment | Habit 1 | Habit 2 | Habit 3 |
|---------|---------|---------|---------|
| Student | 📚 Kitob o'qish (30 min) | 🧘 Meditatsiya (10 min) | ✍️ Kundalik yozish |
| Freelancer | 📧 Inbox zero | 💪 Sport (30 min) | 📚 Kitob o'qish (20 min) |
| Developer | 💻 Side project (30 min) | 📚 Tech article (15 min) | 💪 Sport |
| Entrepreneur | 📰 Yangiliklar o'qish (10 min) | 💪 Sport (30 min) | 📝 Kundalik yozish |
| Other | 💧 Suv ichish (8 stakan) | 📚 Kitob o'qish (20 min) | 💪 Sport |

**Starter Goal (1 ta):**

| Segment | Goal |
|---------|------|
| Student | 📚 Bu semestrda a'lo o'qish |
| Freelancer | 💰 Bu oyda 3 ta loyiha tugatish |
| Developer | 🚀 Yangi texnologiya o'rganish |
| Entrepreneur | 📈 Bu oyda 20% o'sish |
| Other | 🎯 Kundalik rejimni shakllantirish |

### Qatlam 2: Birinchi AI reja — segment + starter data asosida

User birinchi marta AI planner ochganda:
1. Starter tasks + habits allaqachon bor
2. AI ularni ko'radi va vaqt bo'yicha joylashtiradi
3. Qo'shimcha 1-2 ta task tavsiya qiladi
4. Coaching note: "Birinchi kuningiz! Hamma narsani bajarishga urinmang, 2-3 ta eng muhimini tanlang."

### Qatlam 3: Progressive personalization (1-7 kun)

| Kun | Nima o'zgaradi |
|-----|---------------|
| 1-kun | Starter pack. Oddiy mission'lar (1 task bajar, 1 habit logla) |
| 2-kun | User nimani bajardi/bajarmadi ko'rinadi. Mission'lar shunga moslashadi |
| 3-kun | Birinchi streak (3 kun). Coaching: "3 kunlik streak! Davom eting" |
| 5-kun | AI coaching ma'noli bo'ladi (5 kun data bor) |
| 7-kun | AI planner to'liq ishlaydi — real pattern'lar asosida |
| 14-kun | Coaching insights to'liq — burnout detection ishlaydi |

## Texnik Implementation

### Qadam 1: Starter data template'lar (backend)

**Fayl:** `app/services/starter_service.py`

```
STARTER_TASKS = {
    "student": [...],
    "freelancer": [...],
    ...
}

STARTER_HABITS = {
    "student": [...],
    ...
}

STARTER_GOALS = {
    "student": {...},
    ...
}

async def create_starter_pack(db, user_id, segment):
    # 1. Starter tasks yaratish (bugungi sana bilan)
    # 2. Starter habits yaratish
    # 3. Starter goal yaratish
    # 4. Birinchi mission'lar generate qilish
```

### Qadam 2: Onboarding'ga ulash

**Fayl:** `app/bot/handlers/onboarding.py`

Onboarding step 4 (tugallanganda) da `create_starter_pack()` chaqirish.

### Qadam 3: AI planner cold start mode

**Fayl:** `app/ai/prompts/planner.py`

Prompt'ga qo'shimcha:
```
If this is a new user (0-2 days), be gentle:
- Use their starter tasks, don't add many new ones
- Suggest max 1 new task
- Coaching note should be welcoming and simple
- Don't suggest focus sessions longer than 25 min
```

### Qadam 4: Frontend welcome state

**Fayl:** `frontend/src/app/page.tsx`

Yangi user (onboarding_step === 4, created_at < 24h) uchun:
- "Xush kelibsiz!" banner
- "Bu sizning starter rejangiz" label
- Starter tasks/habits special badge bilan

## O'zgarishi kerak bo'lgan fayllar

| Fayl | O'zgartirish |
|------|-------------|
| `services/starter_service.py` | **YANGI** — starter pack template'lar + yaratish logic |
| `bot/handlers/onboarding.py` | Onboarding tugaganda `create_starter_pack()` chaqirish |
| `ai/prompts/planner.py` | Cold start mode qo'shish |
| `frontend/src/app/page.tsx` | Welcome banner yangi user uchun |

## Nima O'ZGARMAYDI

- Task/Habit/Goal CRUD — xuddi shu API ishlatiladi
- AI agent'lar — xuddi shu, faqat prompt'ga cold start instruction qo'shiladi
- XP/Streak/Mission — xuddi shu logic, starter content bilan ham ishlaydi
- Database — yangi jadval kerak emas

## Natija

Yangi user:
1. `/start` → segment tanlaydi
2. Onboarding tugaydi → **avtomatik 3-5 task, 2-3 habit, 1 goal yaratiladi**
3. Home page'da tayyor reja ko'radi — bo'sh emas!
4. AI planner chaqirsa — starter data asosida reja yaratadi
5. 3-7 kunda — real data to'planadi, AI personalized bo'ladi
