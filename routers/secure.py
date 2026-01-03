"""
Secure Router - Demonstrates proper Session Management.
Uses session regeneration to prevent Session Fixation attacks.

Version 2.0 Security Features:
- Session Regeneration on login
- Session TTL (Time-To-Live) - 5 minutes timeout
- User-Agent binding (browser fingerprinting)
- IP address binding
- HttpOnly cookies (XSS protection)
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import html

from database import get_db
from models import User, SessionData
from dependencies import get_user_from_secure_session
from utils import hash_password, verify_password

router = APIRouter(prefix="/secure", tags=["secure"])
templates = Jinja2Templates(directory="templates")

# Session configuration
SESSION_TTL_MINUTES = 5  # Session expires after 5 minutes of inactivity


def generate_secure_session_id() -> str:
    """Generate a cryptographically strong random session ID."""
    return secrets.token_hex(32)


@router.get("/", response_class=HTMLResponse)
async def secure_home(request: Request):
    """Redirect to login page."""
    return RedirectResponse(url="/secure/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def secure_login_page(
    request: Request,
    token: Optional[str] = None  # Token is IGNORED for security
):
    """
    SECURE: Display login page.
    Any token provided in URL is completely IGNORED.
    """
    # NOTE: We intentionally ignore the 'token' parameter
    # This prevents session fixation via URL injection
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "mode": "secure",
            "theme_color": "#198754",  # Green for safe
            "mode_label": "حالت امن",
            "error": None,
            "token": None  # Always None - we ignore URL tokens
        }
    )


@router.post("/login", response_class=HTMLResponse)
async def secure_login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    SECURE: Process login with session regeneration.
    Always generates a new session ID upon successful authentication.
    """
    # Find user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "mode": "secure",
                "theme_color": "#198754",
                "mode_label": "حالت امن",
                "error": "نام کاربری یا رمز عبور اشتباه است",
                "token": None
            }
        )
    
    # SECURITY FIX: Delete any existing session for this user
    old_session_id = request.cookies.get("secure_session")
    if old_session_id:
        old_session = db.query(SessionData).filter(
            SessionData.session_id == old_session_id
        ).first()
        if old_session:
            db.delete(old_session)
            db.commit()
    
    # SECURITY FIX: Always generate a NEW cryptographically strong session ID
    # This is the Session Regeneration that prevents fixation attacks
    new_session_id = generate_secure_session_id()
    
    # VERSION 2.0: Get client fingerprint for session binding
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    
    # Create new session with security binding
    new_session = SessionData(
        session_id=new_session_id,
        user_id=user.id,
        user_agent=user_agent,
        ip_address=client_ip,
        created_at=datetime.utcnow(),
        last_accessed=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    
    response = RedirectResponse(url="/secure/dashboard", status_code=302)
    
    # SECURITY: Set cookie with security flags
    response.set_cookie(
        key="secure_session",
        value=new_session_id,
        httponly=True,      # Prevents JavaScript access (XSS protection)
        samesite="lax",     # CSRF protection
        secure=False,       # Set to True in production with HTTPS
        max_age=SESSION_TTL_MINUTES * 60  # Cookie expiry matches session TTL
    )
    
    return response


@router.get("/register", response_class=HTMLResponse)
async def secure_register_page(request: Request):
    """
    SECURE: Display registration page.
    """
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "mode": "secure",
            "theme_color": "#198754",  # Green for safe
            "mode_label": "حالت امن",
            "error": None,
            "success": None
        }
    )


@router.post("/register", response_class=HTMLResponse)
async def secure_register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    SECURE: Process user registration.
    """
    # Validate password confirmation
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "mode": "secure",
                "theme_color": "#198754",
                "mode_label": "حالت امن",
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
                "mode": "secure",
                "theme_color": "#198754",
                "mode_label": "حالت امن",
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
                "mode": "secure",
                "theme_color": "#198754",
                "mode_label": "حالت امن",
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
            "mode": "secure",
            "theme_color": "#198754",
            "mode_label": "حالت امن",
            "error": None,
            "success": f"کاربر '{username}' با موفقیت ایجاد شد! اکنون می‌توانید وارد شوید."
        }
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def secure_dashboard(
    request: Request,
    user: User = Depends(get_user_from_secure_session),
    db: Session = Depends(get_db)
):
    """Secure dashboard - shows user info and session ID."""
    if not user:
        return RedirectResponse(url="/secure/login", status_code=302)
    
    session_id = request.cookies.get("secure_session", "نامشخص")
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "mode": "secure",
            "theme_color": "#198754",
            "mode_label": "حالت امن",
            "username": user.username,
            "session_id": session_id,
            "logout_url": "/secure/logout"
        }
    )


@router.get("/logout")
async def secure_logout(request: Request, db: Session = Depends(get_db)):
    """Logout and clear session securely."""
    session_id = request.cookies.get("secure_session")
    
    if session_id:
        session = db.query(SessionData).filter(
            SessionData.session_id == session_id
        ).first()
        if session:
            db.delete(session)
            db.commit()
    
    response = RedirectResponse(url="/secure/login", status_code=302)
    response.delete_cookie("secure_session")
    return response


# =============================================================================
# 🟢 SECURE SEARCH ENDPOINT - Version 2.0
# =============================================================================

@router.get("/search", response_class=HTMLResponse)
async def secure_search(
    request: Request,
    q: Optional[str] = None,
    user: User = Depends(get_user_from_secure_session),
    db: Session = Depends(get_db)
):
    """
    🟢 SECURE: Safe search endpoint.
    
    The 'q' parameter is properly ESCAPED before embedding in HTML.
    This prevents XSS attacks.
    
    Security measures:
    1. HTML escaping of user input
    2. HttpOnly cookie (can't be stolen via XSS)
    3. Session binding (User-Agent check)
    """
    
    if not user:
        return RedirectResponse(url="/secure/login", status_code=302)
    
    username = user.username
    session_id = request.cookies.get("secure_session", "نامشخص")
    
    # Get session info for display
    session_data = db.query(SessionData).filter(
        SessionData.session_id == session_id
    ).first()
    
    session_info = {
        "user_agent": session_data.user_agent[:50] + "..." if session_data and session_data.user_agent else "N/A",
        "ip_address": session_data.ip_address if session_data else "N/A",
        "created_at": session_data.created_at.strftime("%H:%M:%S") if session_data and session_data.created_at else "N/A"
    }
    
    # 🟢 SECURITY: Escape user input to prevent XSS!
    safe_query = html.escape(q) if q else ""
    
    search_result_html = ""
    if q:
        search_result_html = f"""
        <div class="alert alert-info">
            <strong>نتایج جستجو برای:</strong> {safe_query}
        </div>
        <div class="card">
            <div class="card-body">
                <p>شما جستجو کردید: <strong>{safe_query}</strong></p>
                <p>متأسفانه نتیجه‌ای یافت نشد.</p>
            </div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>جستجو | نسخه امن</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            * {{ font-family: 'Vazirmatn', sans-serif; }}
            body {{
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
            }}
            .navbar-custom {{ background-color: #198754 !important; }}
            .card-glass {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            .success-banner {{
                background: linear-gradient(135deg, #26de81, #20bf6b);
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
            .security-badge {{
                background: #198754;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark navbar-custom">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/">🔐 آزمایشگاه امنیت نشست</a>
                <div class="d-flex align-items-center">
                    <span class="badge bg-light text-dark me-3 px-3 py-2">حالت امن</span>
                    <a href="/secure/dashboard" class="text-white me-3">داشبورد</a>
                    <a href="/secure/logout" class="text-white">خروج</a>
                </div>
            </div>
        </nav>
        
        <main class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card-glass p-5">
                        <div class="success-banner text-center">
                            <h5>✅ این صفحه امن است!</h5>
                            <small>ورودی کاربر با HTML Escaping پاکسازی می‌شود.</small>
                        </div>
                        
                        <h3 class="text-center mb-4">🔍 جستجوی امن</h3>
                        
                        <div class="mb-3 p-3 bg-light rounded">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong>👤 کاربر:</strong>
                                <span>{username}</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong>🌐 مرورگر:</strong>
                                <span class="security-badge">✅ بایند شده</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong>⏰ زمان ورود:</strong>
                                <span>{session_info['created_at']}</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>🍪 HttpOnly:</strong>
                                <span class="security-badge">✅ فعال</span>
                            </div>
                        </div>
                        
                        <form method="GET" action="/secure/search" class="mb-4">
                            <div class="input-group">
                                <input type="text" name="q" class="form-control form-control-lg" 
                                       placeholder="عبارت جستجو..." value="{safe_query}">
                                <button type="submit" class="btn btn-success btn-lg">جستجو</button>
                            </div>
                        </form>
                        
                        {search_result_html}
                        
                        <hr>
                        
                        <div class="alert alert-success">
                            <h5>🛡️ محافظت‌های امنیتی فعال:</h5>
                            <ul class="mb-0">
                                <li><strong>HTML Escaping:</strong> کاراکترهای خطرناک تبدیل می‌شوند</li>
                                <li><strong>HttpOnly Cookie:</strong> JavaScript نمی‌تواند کوکی را بخواند</li>
                                <li><strong>User-Agent Binding:</strong> سشن به مرورگر بایند شده</li>
                                <li><strong>Session TTL:</strong> سشن بعد از ۵ دقیقه منقضی می‌شود</li>
                            </ul>
                        </div>
                        
                        <div class="text-center mt-4">
                            <a href="/secure/dashboard" class="btn btn-outline-success">
                                بازگشت به داشبورد
                            </a>
                            <a href="/vulnerable/search" class="btn btn-outline-danger">
                                رفتن به نسخه آسیب‌پذیر
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

