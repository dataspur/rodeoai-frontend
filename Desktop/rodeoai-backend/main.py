from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import sys
import logging

from database import engine, get_db, Base
from models import User, ContestantProfile
from schemas import (
    UserCreate, UserResponse, Token,
    ContestantProfileCreate, ContestantProfileUpdate,
    ContestantProfileResponse, PublicContestantProfile
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from taurus_routing import select_model_for_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RodeoAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

class ChatRequest(BaseModel):
    message: str
    model: str = "taurus"

# Root endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "RodeoAI API is running"}

# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/api/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user info"""
    return current_user

# ==================== Contestant Profile Endpoints ====================

@app.post("/api/contestants/me", response_model=ContestantProfileResponse, status_code=status.HTTP_201_CREATED)
def create_contestant_profile(
    profile: ContestantProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create contestant profile for the current user"""
    # Check if profile already exists
    existing_profile = db.query(ContestantProfile).filter(
        ContestantProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PATCH to update.")

    # Create new profile
    db_profile = ContestantProfile(
        user_id=current_user.id,
        **profile.model_dump()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile

@app.patch("/api/contestants/me", response_model=ContestantProfileResponse)
def update_contestant_profile(
    profile_update: ContestantProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update contestant profile for the current user"""
    db_profile = db.query(ContestantProfile).filter(
        ContestantProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")

    # Update profile fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db.commit()
    db.refresh(db_profile)

    return db_profile

@app.get("/api/contestants/me", response_model=ContestantProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's contestant profile"""
    db_profile = db.query(ContestantProfile).filter(
        ContestantProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return db_profile

@app.get("/api/contestants/{username}", response_model=PublicContestantProfile)
def get_public_profile(username: str, db: Session = Depends(get_db)):
    """Get public contestant profile by username"""
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(ContestantProfile).filter(
        ContestantProfile.user_id == user.id
    ).first()

    return PublicContestantProfile(
        username=user.username,
        full_name=user.full_name,
        profile=profile
    )

# ==================== Chat Endpoint (existing) ====================

@app.post("/api/chat/")
async def chat(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Client not ready")

    # TAURUS: Intelligent model routing based on task complexity and tool requirements
    model, analysis = select_model_for_query(request.message)

    # Log model selection for monitoring and optimization
    logger.info(f"TAURUS Routing: {analysis['reasoning']}")
    logger.info(f"Model: {model}, Complexity: {analysis['complexity_score']}/10, "
                f"Tools: {analysis['tool_categories'] if analysis['requires_tools'] else 'None'}")

    system = "You are TAURUS, an advanced rodeo AI assistant powered by DataSpur. You provide expert insights on rodeo training, equipment, strategy, and competition. You can access tools and resources to help contestants, trainers, and rodeo organizers."

    # Adjust token limit based on model complexity
    max_tokens = 2048 if model in ["gpt-4o", "gpt-4"] else 1024

    async def generate():
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": request.message}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
