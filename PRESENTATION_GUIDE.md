# 🎯 راهنمای ارائه - آزمایشگاه امنیت نشست

> این راهنما برای نمایش و ارائه آسیب‌پذیری‌های مدیریت نشست و احراز هویت طراحی شده است.

---

## 📋 خلاصه پروژه

این پروژه یک **آزمایشگاه امنیتی** است که سه نوع آسیب‌پذیری/حمله را نمایش می‌دهد:

| حمله | توضیح | نمایش در پروژه |
|------|-------|----------------|
| **Session Fixation** | مهاجم شناسه نشست را از قبل تعیین می‌کند | ✅ کامل |
| **Session Hijacking** | مهاجم شناسه نشست قربانی را سرقت می‌کند | ✅ کامل |
| **Token Regeneration** | راه‌حل امن برای جلوگیری از حملات | ✅ کامل |

---

## 🚀 راه‌اندازی سریع

### مرحله ۱: اجرای سرور

```powershell
cd "d:\iman\tmp\test prefect"
.venv\Scripts\activate
python main.py
```

### مرحله ۲: دسترسی به برنامه

| نسخه | آدرس |
|------|------|
| صفحه اصلی | http://localhost:8000 |
| نسخه آسیب‌پذیر | http://localhost:8000/vulnerable/login |
| نسخه امن | http://localhost:8000/secure/login |
| ثبت‌نام آسیب‌پذیر | http://localhost:8000/vulnerable/register |
| ثبت‌نام امن | http://localhost:8000/secure/register |

### اطلاعات ورود پیش‌فرض

```
نام کاربری: admin
رمز عبور: 123456
```

---

## 🔴 دمو ۱: حمله Session Fixation

### مفهوم حمله

> مهاجم یک شناسه نشست انتخاب می‌کند و آن را به قربانی می‌دهد. وقتی قربانی لاگین می‌کند، مهاجم با همان شناسه به حساب او دسترسی پیدا می‌کند.

### مراحل نمایش (۵ دقیقه)

#### مرحله ۱: آماده‌سازی
1. **دو مرورگر یا پنجره** باز کنید:
   - مرورگر ۱: نقش **مهاجم** 🔴
   - مرورگر ۲: نقش **قربانی** 🟢

#### مرحله ۲: مهاجم لینک آلوده می‌سازد
در مرورگر مهاجم، این URL را نشان دهید:
```
http://localhost:8000/vulnerable/login?token=HACKER_SESSION_123
```

**توضیح دهید:** مهاجم این لینک را از طریق ایمیل، پیامک یا شبکه اجتماعی به قربانی ارسال می‌کند.

#### مرحله ۳: قربانی روی لینک کلیک می‌کند
در مرورگر قربانی:
1. آدرس بالا را باز کنید
2. با اطلاعات لاگین وارد شوید:
   - نام کاربری: `admin`
   - رمز عبور: `123456`
3. به **داشبورد** منتقل می‌شوید

**به شناسه نشست در داشبورد توجه کنید:** همان `HACKER_SESSION_123` است!

#### مرحله ۴: مهاجم دسترسی پیدا می‌کند
در مرورگر مهاجم:
1. **DevTools** را باز کنید (`F12`)
2. به تب **Console** بروید
3. این دستور را اجرا کنید:
   ```javascript
   document.cookie = "vulnerable_session=HACKER_SESSION_123"
   ```
4. به این آدرس بروید:
   ```
   http://localhost:8000/vulnerable/dashboard
   ```

**نتیجه:** مهاجم بدون دانستن رمز عبور، به حساب قربانی دسترسی پیدا کرد! 💀

---

## 🔵 دمو ۲: حمله Session Hijacking

### مفهوم حمله

> مهاجم شناسه نشست فعال قربانی را سرقت می‌کند (مثلاً از طریق XSS یا شنود شبکه) و با آن به حساب قربانی وارد می‌شود.

### مراحل نمایش (۵ دقیقه)

#### مرحله ۱: قربانی لاگین می‌کند
1. در مرورگر **قربانی**، به آدرس زیر بروید:
   ```
   http://localhost:8000/vulnerable/login
   ```
2. لاگین کنید
3. به داشبورد بروید و **شناسه نشست** را یادداشت کنید

#### مرحله ۲: سرقت شناسه نشست

**سناریوی واقعی:** در دنیای واقعی، مهاجم می‌تواند شناسه را از طریق:
- ✅ حمله XSS (اگر `httpOnly=false` باشد)
- ✅ شنود شبکه (اگر HTTPS نباشد)
- ✅ دسترسی فیزیکی به مرورگر

برای نمایش، در مرورگر قربانی:
1. DevTools → Console
2. اجرا کنید:
   ```javascript
   console.log("شناسه نشست سرقت شده:", document.cookie)
   ```
3. شناسه نشست را کپی کنید

#### مرحله ۳: مهاجم از شناسه سرقتی استفاده می‌کند
در مرورگر **مهاجم** (تب جدید یا Incognito):
1. DevTools → Console
2. شناسه سرقتی را وارد کنید:
   ```javascript
   document.cookie = "vulnerable_session=شناسه_سرقتی"
   ```
3. به داشبورد بروید:
   ```
   http://localhost:8000/vulnerable/dashboard
   ```

**نتیجه:** مهاجم به حساب قربانی دسترسی پیدا کرد!

---

## 🟢 دمو ۳: راه‌حل امن (Token Regeneration)

### مفهوم راه‌حل

> پس از هر احراز هویت موفق، شناسه نشست جدید تولید می‌شود. این کار حملات Session Fixation را بی‌اثر می‌کند.

### مراحل نمایش (۳ دقیقه)

#### تست Session Fixation روی نسخه امن

1. در مرورگر، به آدرس زیر بروید:
   ```
   http://localhost:8000/secure/login?token=HACKER_SESSION_123
   ```
2. لاگین کنید
3. به شناسه نشست در داشبورد نگاه کنید

**نتیجه:** شناسه نشست **کاملاً متفاوت** از `HACKER_SESSION_123` است! ✅

### تفاوت کد

#### ❌ کد آسیب‌پذیر:
```python
# شناسه نشست از کوکی موجود استفاده می‌شود
existing_session_id = request.cookies.get("vulnerable_session")
session_data.user_id = user.id  # فقط کاربر را متصل می‌کنیم
session_id = existing_session_id  # ❌ همان شناسه قبلی!
```

#### ✅ کد امن:
```python
import secrets

# همیشه شناسه جدید تولید می‌شود
new_session_id = secrets.token_hex(32)  # ✅ شناسه تصادفی

# نشست قدیمی حذف می‌شود
if old_session:
    db.delete(old_session)

# نشست جدید ایجاد می‌شود
new_session = SessionData(session_id=new_session_id, user_id=user.id)
```

---

## 🧪 تست خودکار

برای نمایش تست خودکار به مخاطبان:

```powershell
cd "d:\iman\tmp\test prefect"
.venv\Scripts\python test_attack.py
```

### خروجی مورد انتظار:

```
🔴 تست حمله Session Fixation - نسخه آسیب‌پذیر
   ✅ موفق: حمله Session Fixation موفق بود!

🟢 تست حمله Session Fixation - نسخه امن  
   ✅ موفق: Session Regeneration موفق بود!
```

---

## 📊 جدول مقایسه امنیتی

| ویژگی | نسخه آسیب‌پذیر | نسخه امن |
|-------|---------------|----------|
| پذیرش توکن از URL | ✅ بله | ❌ خیر |
| Session Regeneration | ❌ خیر | ✅ بله |
| HttpOnly Cookie | ❌ خیر | ✅ بله |
| SameSite Cookie | Lax | Lax |
| ایمن در برابر Fixation | ❌ | ✅ |
| ایمن در برابر XSS Session Theft | ❌ | ✅ |

---

## 🔧 راهکارهای امنیتی

### ۱. Session Regeneration (ضروری)
```python
# پس از هر لاگین موفق
new_session_id = secrets.token_hex(32)
```

### ۲. HttpOnly Cookie (ضروری)
```python
response.set_cookie(
    key="session",
    value=session_id,
    httponly=True  # JavaScript نمی‌تواند بخواند
)
```

### ۳. Secure Cookie (برای Production)
```python
response.set_cookie(
    key="session",
    value=session_id,
    secure=True  # فقط HTTPS
)
```

### ۴. SameSite Cookie (پیشنهادی)
```python
response.set_cookie(
    key="session",
    value=session_id,
    samesite="strict"  # محافظت CSRF
)
```

### ۵. Session Timeout (پیشنهادی)
```python
response.set_cookie(
    key="session",
    value=session_id,
    max_age=3600  # ۱ ساعت
)
```

---

## 📁 ساختار پروژه

```
test prefect/
├── main.py                 # نقطه ورود برنامه
├── database.py             # اتصال دیتابیس SQLite
├── models.py               # مدل‌های User و SessionData
├── dependencies.py         # توابع کمکی FastAPI
├── utils.py                # توابع هش کردن رمز
├── test_attack.py          # تست خودکار حملات
├── README.md               # مستندات کامل
├── PRESENTATION_GUIDE.md   # این فایل
├── requirements.txt        # وابستگی‌ها
├── routers/
│   ├── vulnerable.py       # منطق آسیب‌پذیر
│   └── secure.py           # منطق امن
└── templates/
    ├── base.html           # قالب پایه
    ├── login.html          # صفحه ورود
    ├── register.html       # صفحه ثبت‌نام
    └── dashboard.html      # داشبورد کاربر
```

---

## ⏱️ زمان‌بندی پیشنهادی ارائه

| بخش | زمان |
|-----|------|
| معرفی و مفاهیم اولیه | ۵ دقیقه |
| دمو Session Fixation | ۵ دقیقه |
| دمو Session Hijacking | ۵ دقیقه |
| دمو راه‌حل امن | ۳ دقیقه |
| تست خودکار | ۲ دقیقه |
| بررسی کد و سوالات | ۵ دقیقه |
| **مجموع** | **۲۵ دقیقه** |

---

## ❓ سوالات متداول

### چرا Session Fixation خطرناک است؟
مهاجم بدون نیاز به دانستن رمز عبور، می‌تواند به حساب کاربر دسترسی پیدا کند.

### Session Hijacking چه تفاوتی با Fixation دارد؟
- **Fixation:** مهاجم شناسه را *قبل* از لاگین به قربانی می‌دهد
- **Hijacking:** مهاجم شناسه را *بعد* از لاگین سرقت می‌کند

### چرا HttpOnly مهم است؟
اگر سایت آسیب‌پذیری XSS داشته باشد، مهاجم نمی‌تواند با JavaScript به کوکی دسترسی پیدا کند.

### آیا HTTPS کافی است؟
خیر! HTTPS فقط از شنود شبکه محافظت می‌کند، نه از Session Fixation.

---

## 📚 منابع

- [OWASP Session Fixation](https://owasp.org/www-community/attacks/Session_fixation)
- [OWASP Session Hijacking](https://owasp.org/www-community/attacks/Session_hijacking_attack)
- [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

## ⚠️ هشدار اخلاقی

> این پروژه **صرفاً برای اهداف آموزشی** ساخته شده است.
> 
> استفاده از این تکنیک‌ها بر روی سیستم‌های دیگران **بدون اجازه، غیرقانونی** است.

---

ساخته شده با ❤️ برای آموزش امنیت وب
