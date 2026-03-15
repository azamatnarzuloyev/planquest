# Task 3: Telegram Bot Foundation — Webhook va Command Handler

**Status:** ✅ Yakunlangan (2026-03-15)
**Estimated:** 9 qadam
**Dependency:** Task 1 ✅, Task 2 ✅
**Output:** Bot `/start` va `/help` komandalarga javob beradi. Webhook FastAPI orqali ishlaydi. Telegram'da bot bilan gaplashish mumkin.

---

## Qadamlar

### Qadam 1: aiogram dependency qo'shish va install
**Nima uchun aiogram?**
- `aiogram 3.x` — eng zamonaviy async Telegram bot framework
- FastAPI bilan yaxshi integratsiya (ikkalasi ham asyncio)
- Webhook mode native support
- Middleware, filter, router pattern'lar bor
- `python-telegram-bot` dan farqi: aiogram to'liq async, FastAPI ga yaqinroq arxitektura

**pyproject.toml ga qo'shish:**
- `aiogram>=3.15.0` — Telegram Bot framework

**Qo'shimcha kerak bo'lishi mumkin:**
- `pydantic` — aiogram ichida allaqachon bor

**Tayyor belgisi:** `pip install aiogram` xatosiz o'rnatiladi, Docker rebuild ishlaydi.

---

### Qadam 2: Bot instance yaratish
**backend/app/core/bot.py:**

```python
# Bot va Dispatcher yaratish
# Bot(token=settings.BOT_TOKEN)
# Dispatcher() — handler'lar ro'yxatga olinadi
# Router() — command handler'lar guruhlash uchun
```

**Muhim:**
- Bot instance global — bir marta yaratiladi, app lifecycle bilan boshqariladi
- Dispatcher — update'larni route qiladi
- Router — handler'larni modul bo'yicha ajratish imkonini beradi
- Bot token `.env` dan olinadi (`settings.BOT_TOKEN`)

**Tayyor belgisi:** `from app.core.bot import bot, dp` import xatosiz ishlaydi.

---

### Qadam 3: Command handler'lar — /start va /help
**backend/app/bot/handlers/commands.py:**

**/start handler:**
```
User /start bosganda:
1. Bot "Salom! Men PlanQuest botman..." deb javob beradi
2. Hozircha oddiy text javob (onboarding flow Task 13 da qilinadi)
3. Reply markup: inline keyboard bilan
   - [Dashboard ochish] → Mini App deep link
   - [Yordam] → /help
```

**/help handler:**
```
User /help bosganda:
Bot komandalar ro'yxatini ko'rsatadi:
  /start — Botni boshlash
  /help — Yordam
  /add — Task qo'shish (Task 11 da)
  /today — Bugungi reja (Task 11 da)
  /habits — Habitlar (Task 11 da)
  /focus — Fokus session (Task 11 da)
  /stats — Statistika (Task 11 da)
```

**Fayl strukturasi:**
```
backend/app/bot/
├── __init__.py
├── handlers/
│   ├── __init__.py
│   └── commands.py    ← /start, /help handler'lar
└── middlewares/
    └── __init__.py
```

**Tayyor belgisi:** Handler'lar router'ga register qilingan, import xatosiz.

---

### Qadam 4: Webhook endpoint — FastAPI route
**backend/app/api/routes/telegram.py:**

```python
# POST /api/telegram/webhook
# 1. Request body'ni olish (Telegram Update JSON)
# 2. aiogram Dispatcher ga feed qilish
# 3. 200 OK qaytarish

# Endpoint:
#   POST /api/telegram/webhook
#   Body: Telegram Update object (JSON)
#   Response: 200 OK (empty yoki {"ok": true})
```

**Muhim nuanslar:**
- Telegram webhook har doim 200 qaytarishni kutadi (aks holda retry qiladi)
- Update ni Dispatcher.feed_webhook_update() ga berish kerak
- Xatolik bo'lsa ham 200 qaytarish (xatolikni log qilish, Telegram'ga error bermash)
- Request body raw JSON sifatida olish (aiogram o'zi parse qiladi)

**Tayyor belgisi:** `POST /api/telegram/webhook` endpoint mavjud, 200 qaytaradi.

---

### Qadam 5: Bot lifecycle — FastAPI lifespan bilan integratsiya
**backend/app/main.py yangilash:**

```python
# Lifespan ga qo'shish:
# Startup:
#   1. Redis init (mavjud)
#   2. Bot webhook o'rnatish (set_webhook)
#   3. Dispatcher ga router'larni register qilish
#
# Shutdown:
#   1. Bot webhook o'chirish (delete_webhook)
#   2. Bot session yopish
#   3. Redis yopish (mavjud)
```

**Webhook URL:**
- `settings.WEBHOOK_URL` dan olinadi
- Development da: ngrok yoki cloudflared tunnel ishlatiladi
- Production da: real domain URL

**Eslatma:** Agar `WEBHOOK_URL` bo'sh bo'lsa — webhook o'rnatilmaydi (local dev uchun). Bu holda bot faqat API orqali test qilinadi.

**Tayyor belgisi:** Server start bo'lganda webhook avtomatik o'rnatiladi (agar URL berilgan bo'lsa).

---

### Qadam 6: Webhook registration script
**backend/app/bot/setup.py:**

```python
# set_webhook() — botga webhook URL berish
# delete_webhook() — webhook o'chirish
# get_webhook_info() — joriy webhook ma'lumotlari

# Bu funksiyalar lifespan da chaqiriladi
# Yoki alohida script sifatida: python -m app.bot.setup
```

**Yoki Makefile command:**
```makefile
webhook-set:
    docker-compose exec -T backend python -c "..."
webhook-info:
    docker-compose exec -T backend python -c "..."
```

**Tayyor belgisi:** Webhook URL o'rnatilishi yoki o'chirilishi mumkin.

---

### Qadam 7: Bot router'ni FastAPI app ga ulash
**backend/app/main.py yangilash:**

- Telegram webhook router'ni include qilish: `app.include_router(telegram_router, prefix="/api/telegram")`
- Bot handler router'larni Dispatcher'ga register qilish
- Barcha import'lar to'g'ri ishlashi

**Tayyor belgisi:** `/api/telegram/webhook` endpoint mavjud va ishlaydi.

---

### Qadam 8: Local development uchun test (webhook'siz)
**Muammo:** Local dev da webhook ishlamaydi (Telegram serverdan localhost'ga request yubora olmaydi).

**Yechim variantlari:**
1. **ngrok/cloudflared** — tunnel ochib, public URL olish
2. **Polling mode** — development uchun long polling rejim
3. **Manual test** — `/api/telegram/webhook` ga curl bilan Update JSON yuborish

**Test uchun curl command:**
```bash
curl -X POST http://localhost:8000/api/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "from": {"id": 12345, "is_bot": false, "first_name": "Test"},
      "chat": {"id": 12345, "type": "private"},
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

Bu test orqali handler ishlayotganini tekshirish mumkin (bot javob yubora olmaydi chunki fake chat_id, lekin handler xatosiz ishlashi kerak).

**Tayyor belgisi:** Curl bilan test qilganda 200 OK qaytadi, logda handler ishlayotgani ko'rinadi.

---

### Qadam 9: Verification
**Tekshirish ro'yxati:**

1. `docker-compose up -d --build` → backend xatosiz start bo'ladi
2. `curl -s http://localhost:8000/health` → `{"status":"ok"}`
3. `curl -X POST http://localhost:8000/api/telegram/webhook -H "Content-Type: application/json" -d '{"update_id":1}'` → 200 OK
4. Fake `/start` update yuborilganda logda handler ishlayotgani ko'rinadi
5. Fake `/help` update yuborilganda logda handler ishlayotgani ko'rinadi
6. `BOT_TOKEN` bo'sh bo'lganda ham server crash qilmaydi (graceful handling)
7. Bot instance yaratilganini tekshirish: `docker-compose logs backend | grep -i bot`

**Real Telegram test (agar token bor bo'lsa):**
1. Ngrok tunnel ochish: `ngrok http 8000`
2. `.env` da `WEBHOOK_URL=https://xxx.ngrok.io/api/telegram/webhook` o'rnatish
3. Backend restart
4. Telegram'da botga `/start` yozish → javob keladi
5. `/help` yozish → komandalar ro'yxati keladi

**Agar hamma narsa ishlasa — Task 3 yakunlangan. ✅**

---

## Yakuniy fayl strukturasi (Task 3 tugagandan keyin)

```
backend/app/
├── bot/
│   ├── __init__.py
│   ├── setup.py           ← webhook registration
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── commands.py    ← /start, /help
│   └── middlewares/
│       └── __init__.py
├── api/routes/
│   ├── health.py          ← (mavjud)
│   └── telegram.py        ← POST /api/telegram/webhook
├── core/
│   ├── bot.py             ← Bot, Dispatcher instance
│   ├── database.py        ← (mavjud)
│   └── redis.py           ← (mavjud)
└── main.py                ← (yangilangan — bot lifecycle qo'shilgan)
```

---

## Eslatmalar

- **Onboarding flow** (segment tanlash, birinchi task yaratish) bu taskda yo'q — Task 13 da qilinadi
- **User auto-registration** (bot orqali kelgan user'ni DB ga saqlash) bu taskda yo'q — Task 4 da qilinadi
- **Task/Habit bot command'lari** (`/add`, `/today`, `/habits`) — Task 11 da qilinadi
- Bu taskda bot faqat **skeleton** — `/start` va `/help` ga oddiy text javob beradi
- **Real Telegram test** faqat bot token va webhook URL bor bo'lganda mumkin
- Development uchun **curl test** yetarli
