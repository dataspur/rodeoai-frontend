"""Database models for RodeoAI backend."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float, Index
from sqlalchemy.dialects.postgresql import JSONB
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

    # Payment fields
    stripe_customer_id = Column(String(255), unique=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


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


class Payment(Base):
    """Payment model to track rodeo entry payments and other transactions."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True, index=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), default="usd")
    status = Column(String(50), index=True)  # succeeded, pending, failed, canceled
    description = Column(Text)
    metadata = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="payments")


class Subscription(Base):
    """Subscription model for Pro and Premium plans."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)
    plan = Column(String(50), nullable=False)  # free, pro, premium
    status = Column(String(50), index=True)  # active, canceled, past_due, trialing
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")


class DeviceFingerprint(Base):
    """Track devices uploading images for product recognition."""
    __tablename__ = "device_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)

    # Device metadata
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    software = Column(String(200))

    # Tracking
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    upload_count = Column(Integer, default=1)

    # Associated user (if authenticated)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Additional metadata (JSONB for PostgreSQL, Text for SQLite)
    metadata = Column(Text)  # Will store JSON string

    __table_args__ = (
        Index('idx_device_user', 'device_id', 'user_id'),
    )


class ImageUpload(Base):
    """Track all image uploads for product recognition."""
    __tablename__ = "image_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String(64), ForeignKey("device_fingerprints.device_id"))

    # Image info
    image_hash = Column(String(64), index=True)  # Perceptual hash
    file_path = Column(String(500))
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # EXIF metadata
    exif_data = Column(Text)  # JSON string

    # GPS if available
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Recognition results (cached)
    recognition_results = Column(Text)  # JSON string
    processing_time_ms = Column(Integer)

    __table_args__ = (
        Index('idx_upload_device_time', 'device_id', 'upload_timestamp'),
        Index('idx_upload_hash', 'image_hash'),
    )


class ProductCatalog(Base):
    """Master product catalog for visual recognition."""
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)

    # Product identity
    brand = Column(String(100), index=True, nullable=False)
    model = Column(String(200), index=True, nullable=False)
    category = Column(String(50), index=True)  # boots, hats, vests, etc.
    subcategory = Column(String(100))

    # Product details
    description = Column(String(1000))
    sku = Column(String(100), unique=True)
    upc = Column(String(20), index=True)

    # Visual data (stored as JSON strings)
    image_urls = Column(Text)  # JSON array of product images
    visual_embedding = Column(Text)  # Vector embedding for similarity search

    # Metadata
    attributes = Column(Text)  # JSON: color, size, material, etc.
    keywords = Column(Text)  # JSON: search keywords

    # Pricing (current best price - updated frequently)
    current_best_price = Column(Float)
    msrp = Column(Float)

    # Priority for scraping (high priority products scraped more frequently)
    priority_level = Column(String(20), default="normal")  # high, normal, low

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_product_brand_model', 'brand', 'model'),
        Index('idx_product_category', 'category', 'subcategory'),
    )


class ProductPrice(Base):
    """Price history across different stores."""
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product_catalog.id"), index=True)

    # Store info
    store_name = Column(String(100), index=True)
    store_url = Column(String(500))
    product_url = Column(String(500))

    # Price data
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # If on sale
    is_on_sale = Column(Boolean, default=False)
    sale_end_date = Column(DateTime(timezone=True), nullable=True)

    # Availability
    in_stock = Column(Boolean, default=True)
    stock_level = Column(String(50))  # "low", "medium", "high", or actual number

    # Tracking
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_verified = Column(DateTime(timezone=True))

    # Metadata (stored as JSON string)
    shipping_info = Column(Text)  # Free shipping, delivery time, etc.

    __table_args__ = (
        Index('idx_price_product_store', 'product_id', 'store_name'),
        Index('idx_price_scraped', 'scraped_at'),
    )
