"""Database models for RodeoAI backend."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class SkillLevel(str, enum.Enum):
    """User skill levels for personalized responses."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class User(Base):
    """User model for authentication and profiles."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    oauth_provider = Column(String(50))  # 'google', 'facebook', etc.
    oauth_id = Column(String(255), unique=True)
    skill_level = Column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER)
    preferences = Column(Text)  # JSON string for additional preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model to store chat sessions."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous users
    title = Column(String(500), default="New Chat")
    model = Column(String(100), default="gpt-4o-mini")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_archived = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Message model to store individual chat messages."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    model = Column(String(100))  # Model used for assistant messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tokens_used = Column(Integer)  # Track token usage for cost analysis

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan")


class Feedback(Base):
    """Feedback model to store user ratings of assistant responses."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous feedback
    rating = Column(String(20))  # 'positive' or 'negative'
    comment = Column(Text)  # Optional detailed feedback
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    message = relationship("Message", back_populates="feedback")
    user = relationship("User", back_populates="feedback")


class RateLimit(Base):
    """Rate limiting tracker for API calls."""
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), index=True, nullable=False)  # IP address or user ID
    endpoint = Column(String(255), index=True)
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
