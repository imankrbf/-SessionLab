"""
Secure Router - Demonstrates proper Session Management.
Uses session regeneration to prevent Session Fixation attacks.
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import User, SessionData
from dependencies import get_user_from_secure_session
from utils import hash_password, verify_password

router = APIRouter(prefix="/secure", tags=["secure"])
templates = Jinja2Templates(directory="templates")


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
    
    # Create new session with the fresh ID
    new_session = SessionData(session_id=new_session_id, user_id=user.id)
    db.add(new_session)
    db.commit()
    
    response = RedirectResponse(url="/secure/dashboard", status_code=302)
    
    # SECURITY: Set cookie with security flags
    response.set_cookie(
        key="secure_session",
        value=new_session_id,
        httponly=True,      # Prevents JavaScript access (XSS protection)
        samesite="lax",     # CSRF protection
        secure=False        # Set to True in production with HTTPS
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
