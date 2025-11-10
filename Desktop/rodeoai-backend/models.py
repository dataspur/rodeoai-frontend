from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_pro = Column(Boolean, default=False)  # Pro tier subscription
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    contestant_profile = relationship("ContestantProfile", back_populates="user", uselist=False)


class ContestantProfile(Base):
    __tablename__ = "contestant_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Social Handles (store just the username/handle for cleaner data)
    instagram = Column(String(100), nullable=True)
    facebook = Column(String(255), nullable=True)  # Full URL might be safer for FB
    snapchat = Column(String(100), nullable=True)
    tiktok = Column(String(100), nullable=True)
    x_twitter = Column(String(100), nullable=True)
    youtube = Column(String(255), nullable=True)

    # Rodeo Info
    hometown = Column(String(100), nullable=True)
    events = Column(String(255), nullable=True)  # e.g., "Team Roping (Header), Calf Roping"
    bio = Column(Text, nullable=True)

    # Optional: Add verification status
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="contestant_profile")
