"""
Supabase client configuration and helper functions
"""

import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Initialize Supabase client
supabase: Optional[Client] = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    else:
        logger.warning("Supabase credentials not found in environment variables")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise Exception("Supabase client not initialized. Check environment variables.")
    return supabase


async def verify_supabase_token(token: str) -> dict:
    """
    Verify Supabase JWT token and return user data

    Args:
        token: Supabase access token from frontend

    Returns:
        dict with user information

    Raises:
        Exception if token is invalid
    """
    try:
        client = get_supabase()
        user = client.auth.get_user(token)

        if user and user.user:
            return {
                "id": user.user.id,
                "email": user.user.email,
                "user_metadata": user.user.user_metadata,
                "app_metadata": user.user.app_metadata,
            }
        else:
            raise Exception("Invalid token or user not found")

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise Exception(f"Authentication failed: {str(e)}")


async def get_user_from_supabase(user_id: str):
    """
    Get user details from Supabase by user ID

    Args:
        user_id: Supabase user UUID

    Returns:
        User data from Supabase
    """
    try:
        client = get_supabase()
        response = client.table('users').select('*').eq('id', user_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    except Exception as e:
        logger.error(f"Failed to get user from Supabase: {e}")
        return None


async def sync_user_to_local_db(supabase_user: dict, db):
    """
    Sync Supabase user to local PostgreSQL database

    Args:
        supabase_user: User data from Supabase
        db: SQLAlchemy database session

    Returns:
        Local user record
    """
    from models import User
    from sqlalchemy import update

    try:
        # Check if user exists in local database
        existing_user = db.query(User).filter(
            User.email == supabase_user.get('email')
        ).first()

        if existing_user:
            # Update existing user
            existing_user.is_active = True
            db.commit()
            return existing_user
        else:
            # Create new user from Supabase data
            new_user = User(
                email=supabase_user.get('email'),
                username=supabase_user.get('user_metadata', {}).get('username') or
                         supabase_user.get('email').split('@')[0],
                full_name=supabase_user.get('user_metadata', {}).get('full_name'),
                hashed_password='',  # Not used with Supabase auth
                is_active=True,
                is_pro=False  # Default to free tier
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

    except Exception as e:
        logger.error(f"Failed to sync user to local DB: {e}")
        db.rollback()
        raise
