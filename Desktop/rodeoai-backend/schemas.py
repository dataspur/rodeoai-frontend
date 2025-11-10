from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_pro: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Contestant Profile Schemas
class ContestantProfileBase(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    snapchat: Optional[str] = None
    tiktok: Optional[str] = None
    x_twitter: Optional[str] = None
    youtube: Optional[str] = None
    hometown: Optional[str] = None
    events: Optional[str] = None
    bio: Optional[str] = None

class ContestantProfileCreate(ContestantProfileBase):
    pass

class ContestantProfileUpdate(ContestantProfileBase):
    pass

class ContestantProfileResponse(ContestantProfileBase):
    id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Combined response for public profile view
class PublicContestantProfile(BaseModel):
    username: str
    full_name: Optional[str] = None
    profile: Optional[ContestantProfileResponse] = None

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
