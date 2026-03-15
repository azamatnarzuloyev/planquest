# Task 4: Auth System — Telegram initData Verification + JWT

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 10 qadam
**Dependency:** Task 2 ✅, Task 3 ✅
**Output:** Mini App `initData` yuborsa → JWT token oladi. Bot orqali kelgan user → auto-register. Protected endpoint'lar faqat JWT bilan ishlaydi. `GET /api/users/me` current user qaytaradi.

---

## Auth System Arxitekturasi

PlanQuest'da **2 ta auth flow** bor — ikkalasi ham Telegram'ga asoslangan:

```
Flow 1: Bot → Auto-registration (server-side)
═══════════════════════════════════════════════
User /start bosadi
    → Telegram webhook update keladi
    → update.message.from_user dan telegram_id, first_name, username olinadi
    → DB da telegram_id bilan user qidiriladi
    → Yo'q bo'lsa → yangi user yaratiladi + user_settings yaratiladi
    → Bor bo'lsa → first_name/username yangilanadi (Telegram'da o'zgargan bo'lishi mumkin)
    → Handler ishlaydi (user konteksti bilan)

Flow 2: Mini App → initData → JWT (client-side)
═══════════════════════════════════════════════
User Mini App ochadi
    → Telegram WebApp.initData ni oladi (query string)
    → Frontend POST /api/auth/telegram ga initData yuboradi
    → Backend initData ni HMAC-SHA256 bilan verify qiladi
    → initData ichidan user ma'lumotlarni parse qiladi
    → DB da user qidiriladi (yoki yaratiladi)
    → JWT token generatsiya qilinadi
    → Frontend JWT ni saqlaydi (localStorage)
    → Keyingi requestlarda Authorization: Bearer <token> header yuboriladi
```

### Nima uchun JWT?
- Mini App har bir API request da initData yuborishga to'g'ri kelmaydi
- JWT stateless — backend har safar DB ga murojaat qilmaydi
- Token expire bo'lganda re-auth qilinadi
- Token ichida: `user_id`, `telegram_id`, `exp` (expiry time)

### Nima uchun initData verification?
- Telegram Mini App `initData` ni cryptographic sign qiladi (BOT_TOKEN asosida)
- Biz verify qilib, user'ning haqiqiy Telegram user ekanini tasdiqlaymiz
- Bu man-in-the-middle attack'lardan himoya qiladi
- initData ichida: `user.id`, `user.first_name`, `user.username`, `auth_date`, `hash`

---

## Qadamlar

### Qadam 1: PyJWT dependency qo'shish
**pyproject.toml ga qo'shish:**
- `pyjwt>=2.9.0` — JWT token create/verify

**Tayyor belgisi:** Docker rebuild, `import jwt` xatosiz ishlaydi.

---

### Qadam 2: Telegram initData verification utility
**backend/app/core/security.py:**

Telegram Mini App initData verification algoritmi (rasmiy Telegram docs bo'yicha):

```
1. initData query string ni parse qilish (key=value&key=value)
2. "hash" parametrni ajratib olish
3. Qolgan parametrlarni alphabetical sort qilish
4. "\n" bilan join qilish → data_check_string
5. HMAC-SHA256(key="WebAppData", msg=BOT_TOKEN) → secret_key
6. HMAC-SHA256(key=secret_key, msg=data_check_string) → calculated_hash
7. calculated_hash == hash → Valid!
8. auth_date tekshirish — 24 soatdan eski bo'lsa reject
```

**Funksiyalar:**
```python
def verify_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
    """
    initData string ni verify qiladi.
    Valid bo'lsa → parsed user data qaytaradi.
    Invalid bo'lsa → None qaytaradi.
    """

def parse_init_data_user(init_data_dict: dict) -> dict:
    """
    Verified initData dan user ma'lumotlarni extract qiladi.
    Returns: {telegram_id, first_name, last_name, username, ...}
    """
```

**Tayyor belgisi:** Test bilan: fake initData yuborilsa None qaytadi, to'g'ri sign qilingan initData yuborilsa user data qaytadi.

---

### Qadam 3: JWT token utility
**backend/app/core/security.py (davom):**

```python
def create_access_token(user_id: str, telegram_id: int) -> str:
    """
    JWT token yaratadi.
    Payload:
      sub: user_id (UUID string)
      telegram_id: int
      exp: now + 7 days
      iat: now
    Secret: settings.SECRET_KEY
    Algorithm: HS256
    """

def verify_access_token(token: str) -> dict | None:
    """
    JWT token ni verify qiladi.
    Valid bo'lsa → payload qaytaradi.
    Expired/Invalid bo'lsa → None qaytaradi.
    """
```

**Token expire:** 7 kun (productivity app — user har kuni kiradi, uzun expire OK).

**Tayyor belgisi:** Token yaratiladi, verify qilinadi, expire qilingan token reject bo'ladi.

---

### Qadam 4: User service — DB operations
**backend/app/services/user_service.py:**

```python
async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    """telegram_id bo'yicha user topish."""

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """UUID bo'yicha user topish."""

async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """
    Yangi user yaratish + UserSettings avtomatik yaratish.
    1. User insert
    2. UserSettings insert (default values)
    3. referral_code generatsiya (8 char random)
    4. commit
    5. return user with settings
    """

async def get_or_create_user(db: AsyncSession, telegram_id: int, first_name: str, last_name: str | None, username: str | None) -> tuple[User, bool]:
    """
    User topish yoki yaratish.
    Returns: (user, is_new)
    - is_new=True → yangi user yaratildi
    - is_new=False → mavjud user topildi (first_name/username yangilandi)
    """

async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    """User ma'lumotlarini yangilash."""
```

**Tayyor belgisi:** User yaratish, topish, yangilash ishlaydi. UserSettings avtomatik yaratiladi.

---

### Qadam 5: Auth endpoint — POST /api/auth/telegram
**backend/app/api/routes/auth.py:**

```python
# POST /api/auth/telegram
# Request body: {"init_data": "query_string_from_telegram"}
#
# Flow:
# 1. init_data ni verify_telegram_init_data() bilan tekshirish
# 2. Agar invalid → 401 Unauthorized
# 3. User ma'lumotlarni parse qilish
# 4. get_or_create_user() — DB dan topish yoki yaratish
# 5. JWT token yaratish
# 6. Response: {
#      "access_token": "eyJ...",
#      "token_type": "bearer",
#      "user": UserResponse
#    }
```

**Pydantic schemas:**
```python
class AuthRequest(BaseModel):
    init_data: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

**Tayyor belgisi:** `POST /api/auth/telegram` valid initData bilan → JWT + user qaytaradi.

---

### Qadam 6: Auth middleware — get_current_user dependency
**backend/app/api/deps.py:**

```python
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency — protected endpoint'lar uchun.

    1. Authorization header dan Bearer token olish
    2. Token ni verify_access_token() bilan tekshirish
    3. Token ichidan user_id olish
    4. DB dan user topish
    5. User topilmasa yoki active emas → 401
    6. User qaytarish

    Usage:
        @router.get("/me")
        async def get_me(user: User = Depends(get_current_user)):
            return user
    """
```

**Xatolik holatlari:**
- Token yo'q → 401 `{"detail": "Not authenticated"}`
- Token invalid → 401 `{"detail": "Invalid token"}`
- Token expired → 401 `{"detail": "Token expired"}`
- User topilmadi → 401 `{"detail": "User not found"}`
- User inactive → 403 `{"detail": "User is inactive"}`

**Tayyor belgisi:** Token yo'q/invalid/expired bo'lganda 401 qaytadi, valid token bilan user qaytadi.

---

### Qadam 7: User endpoints — /api/users/me
**backend/app/api/routes/users.py:**

```python
# GET /api/users/me
# Protected endpoint — JWT kerak
# Returns: UserResponse (current user)

# PATCH /api/users/me
# Protected endpoint — JWT kerak
# Body: UserUpdate (segment, timezone, language, first_name, last_name)
# Returns: UserResponse (yangilangan user)

# GET /api/users/me/settings
# Protected endpoint
# Returns: UserSettingsResponse

# PATCH /api/users/me/settings
# Protected endpoint
# Body: UserSettingsUpdate (reminder times, quiet hours, theme)
# Returns: UserSettingsResponse
```

**Tayyor belgisi:** JWT bilan `/api/users/me` current user qaytaradi, PATCH bilan yangilash ishlaydi.

---

### Qadam 8: Bot middleware — auto-registration
**backend/app/bot/middlewares/auth.py:**

```python
class AuthMiddleware(BaseMiddleware):
    """
    Aiogram middleware — har bir bot update da:
    1. update.message.from_user dan telegram_id, first_name, username olish
    2. get_or_create_user() — DB dan topish yoki yaratish
    3. User object ni handler'ga data["user"] sifatida berish

    Handler'larda:
        async def cmd_start(message: Message, user: User):
            # user — DB dagi User object
    """
```

**Bu middleware barcha handler'larga user inject qiladi.**

Keyin Dispatcher'ga middleware register qilish:
```python
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())
```

**Tayyor belgisi:** Bot orqali `/start` bosilganda user avtomatik DB ga saqlanadi.

---

### Qadam 9: Testlar
**backend/tests/test_auth.py:**

```python
# Test 1: initData verification — valid signature
# Test 2: initData verification — invalid signature → None
# Test 3: initData verification — expired auth_date → None
# Test 4: JWT create → verify → payload match
# Test 5: JWT expired → verify → None
# Test 6: POST /api/auth/telegram — invalid initData → 401
# Test 7: GET /api/users/me — no token → 401
# Test 8: GET /api/users/me — valid token → 200 + user data
# Test 9: PATCH /api/users/me — update segment → 200
# Test 10: User auto-create — get_or_create_user → new user + settings
```

**Tayyor belgisi:** Barcha testlar yashil.

---

### Qadam 10: Verification
**Tekshirish ro'yxati:**

1. Backend xatosiz start bo'ladi
2. `POST /api/auth/telegram` invalid initData bilan → 401
3. `GET /api/users/me` tokensiz → 401
4. Bot orqali `/start` → DB da yangi user paydo bo'ladi:
   ```sql
   SELECT telegram_id, first_name, username FROM users;
   ```
5. `GET /api/users/me` valid JWT bilan → 200 + user data
6. `PATCH /api/users/me` bilan segment o'zgartirish → DB da yangilanadi
7. `GET /api/users/me/settings` → default settings qaytadi
8. `PATCH /api/users/me/settings` bilan reminder time o'zgartirish → ishlaydi
9. `user_settings` jadvalida user uchun avtomatik row yaratilganini tekshirish
10. Expired JWT bilan request → 401

**Agar hamma narsa ishlasa — Task 4 yakunlangan. ✅**

---

## Yakuniy fayl strukturasi (Task 4 tugagandan keyin)

```
backend/app/
├── api/
│   ├── deps.py                    ← get_current_user dependency (YANGI)
│   └── routes/
│       ├── auth.py                ← POST /api/auth/telegram (YANGI)
│       ├── health.py              ← (mavjud)
│       ├── telegram.py            ← (mavjud)
│       └── users.py               ← GET/PATCH /api/users/me (YANGI)
├── bot/
│   ├── handlers/
│   │   └── commands.py            ← (yangilangan — user inject)
│   └── middlewares/
│       ├── __init__.py
│       └── auth.py                ← Bot auth middleware (YANGI)
├── core/
│   ├── bot.py                     ← (yangilangan — middleware register)
│   ├── database.py                ← (mavjud)
│   ├── redis.py                   ← (mavjud)
│   └── security.py                ← initData verify, JWT utils (YANGI)
├── services/
│   └── user_service.py            ← User DB operations (YANGI)
├── config.py                      ← (yangilangan — JWT settings qo'shiladi)
└── main.py                        ← (yangilangan — auth router include)

backend/tests/
├── test_health.py                 ← (mavjud)
└── test_auth.py                   ← Auth testlar (YANGI)
```

---

## Security eslatmalar

- **initData hash** — HMAC-SHA256 bilan verify qilinadi, forge qilib bo'lmaydi
- **auth_date** — 24 soatdan eski initData reject qilinadi (replay attack himoya)
- **JWT SECRET_KEY** — production da kuchli random key ishlatilishi shart
- **JWT expire** — 7 kun, keyin re-auth kerak (Mini App ochilganda auto re-auth)
- **Bot middleware** — har bir update da user DB dan olinadi (cache qo'shish mumkin keyinroq)
- **No password** — bu tizimda parol yo'q, faqat Telegram identity ishlatiladi
