"""
Dependency injection functions for session management.
"""
from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, SessionData


def get_user_from_vulnerable_session(
    request: Request, 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Retrieve user from the vulnerable session cookie.
    This is used in the vulnerable app routes.
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
    Retrieve user from the secure session cookie.
    This is used in the secure app routes.
    """
    session_id = request.cookies.get("secure_session")
    if not session_id:
        return None
    
    session_data = db.query(SessionData).filter(
        SessionData.session_id == session_id
    ).first()
    
    if session_data and session_data.user_id:
        return db.query(User).filter(User.id == session_data.user_id).first()
    
    return None
