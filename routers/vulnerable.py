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
