"""
SQLAlchemy models for User and SessionData tables.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    User model for storing user credentials.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationship to sessions
    sessions = relationship("SessionData", back_populates="user")


class SessionData(Base):
    """
    SessionData model for storing active sessions.
    This is used instead of server-side session middleware 
    to demonstrate session fixation vulnerabilities.
    
    Version 2.0 additions:
    - user_agent: For browser binding (secure mode)
    - ip_address: For IP binding (secure mode)
    - last_accessed: For session activity tracking
    """
    __tablename__ = "sessions"

    session_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    data = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Security binding fields (used in secure mode)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
