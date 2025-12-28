import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    get_current_user,
)
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse, TokenRefresh
from jose import jwt, JWTError
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = hash_password(user_data.password)
    db_user = User(email=user_data.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User registered: {db_user.email}")

    # Return tokens
    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User logged in: {user.email}")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token_data: TokenRefresh):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(token_data.refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: int = int(payload.get("sub"))
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
