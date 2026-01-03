"""
Dependency injection functions for session management.

Version 2.0 Security Features:
- Session TTL validation (5 minutes)
- User-Agent binding check
- IP address binding check
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, SessionData

# Session configuration
SESSION_TTL_MINUTES = 5  # Session expires after 5 minutes


def get_user_from_vulnerable_session(
    request: Request, 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Retrieve user from the vulnerable session cookie.
    This is used in the vulnerable app routes.
    
    ⚠️ VULNERABLE: No additional security checks!
    """
    session_id = request.cookies.get("vulnerable_session")
    if not session_id:
        return None
    
    session_data = db.query(SessionData).filter(
        SessionData.session_id == session_id
    ).first()
    
    if session_data and session_data.user_id:
        return db.query(User).filter(User.id == session_data.user_id).first()
    
    return None


def get_user_from_secure_session(
    request: Request, 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Retrieve user from the secure session cookie with full validation.
    
    ✅ SECURE: Includes multiple security checks:
    1. Session exists
    2. Session TTL (not expired)
    3. User-Agent binding (same browser)
    4. IP address binding (optional - can be too strict)
    """
    session_id = request.cookies.get("secure_session")
    if not session_id:
        return None
    
    session_data = db.query(SessionData).filter(
        SessionData.session_id == session_id
    ).first()
    
    if not session_data or not session_data.user_id:
        return None
    
    # SECURITY CHECK 1: Session TTL (Time-To-Live)
    if session_data.created_at:
        session_age = datetime.utcnow() - session_data.created_at
        if session_age > timedelta(minutes=SESSION_TTL_MINUTES):
            # Session expired - delete it
            print(f"⏰ Session expired for session_id: {session_id[:20]}...")
            db.delete(session_data)
            db.commit()
            return None
    
    # SECURITY CHECK 2: User-Agent Binding
    current_user_agent = request.headers.get("user-agent", "unknown")
    if session_data.user_agent and session_data.user_agent != current_user_agent:
        # User-Agent mismatch - possible session hijacking!
        print(f"🚨 User-Agent mismatch detected!")
        print(f"   Stored: {session_data.user_agent[:50]}...")
        print(f"   Current: {current_user_agent[:50]}...")
        print(f"   ⚠️ Possible session hijacking attempt!")
        # Invalidate the suspicious session
        db.delete(session_data)
        db.commit()
        return None
    
    # SECURITY CHECK 3: IP Address Binding (optional - commented out as it can be too strict)
    # current_ip = request.client.host if request.client else "unknown"
    # if session_data.ip_address and session_data.ip_address != current_ip:
    #     print(f"🚨 IP address mismatch! Stored: {session_data.ip_address}, Current: {current_ip}")
    #     db.delete(session_data)
    #     db.commit()
    #     return None
    
    # Update last_accessed timestamp
    session_data.last_accessed = datetime.utcnow()
    db.commit()
    
    return db.query(User).filter(User.id == session_data.user_id).first()


def get_session_info(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Get detailed session information for dashboard display.
    Returns session metadata including TTL remaining, user-agent, etc.
    """
    session_id = request.cookies.get("secure_session")
    if not session_id:
        return None
    
    session_data = db.query(SessionData).filter(
        SessionData.session_id == session_id
    ).first()
    
    if not session_data:
        return None
    
    # Calculate session age and remaining TTL
    session_age = datetime.utcnow() - session_data.created_at if session_data.created_at else timedelta(0)
    remaining_seconds = max(0, (SESSION_TTL_MINUTES * 60) - session_age.total_seconds())
    
    return {
        "session_id": session_id,
        "created_at": session_data.created_at,
        "last_accessed": session_data.last_accessed,
        "session_age_seconds": int(session_age.total_seconds()),
        "remaining_seconds": int(remaining_seconds),
        "user_agent": session_data.user_agent,
        "ip_address": session_data.ip_address,
        "is_expired": remaining_seconds <= 0
    }

