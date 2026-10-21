"""
DataPulse - Local Authentication Module.

Features:
- Secure Argon2 password hashing
- JWT access tokens
- User registration and login
- Current-user verification
- Logout support
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from db.connection import get_engine, get_session_factory
from db.models import User


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)

JWT_SECRET = os.getenv("DATAPULSE_JWT_SECRET")

if not JWT_SECRET:
    JWT_SECRET = secrets.token_urlsafe(48)
    print(
        "WARNING: DATAPULSE_JWT_SECRET is not configured. "
        "Sessions will be invalidated when the backend restarts."
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60


def get_auth_db():
    """Provide a database session for authentication."""
    factory = get_session_factory(get_engine())
    db = factory()

    try:
        yield db
    finally:
        db.close()


AuthDB = Annotated[Session, Depends(get_auth_db)]


class RegisterRequest(BaseModel):
    """Input required to create an account."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Input required to sign in."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Public user information; never includes password hashes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """Output returned upon successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


def create_access_token(user_id: int) -> str:
    """Create a signed, expiring access token."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: AuthDB,
) -> User:
    """Validate a bearer token and return its active user."""

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required or session expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise unauthorized

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise unauthorized

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: AuthDB):
    """Register a new user account."""

    email = str(payload.email).strip().lower()

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        hashed_password=password_hash.hash(payload.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create this account. Please try again.",
        )

    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: AuthDB):
    """Verify credentials and return an access token."""

    email = str(payload.email).strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if (
        user is None
        or not password_hash.verify(payload.password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_MINUTES * 60,
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    """Return the authenticated user's public profile."""
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser, response: Response):
    """
    Acknowledge logout.

    Bearer JWTs are stateless. The frontend must discard its token.
    The token remains usable until expiry unless server-side revocation
    is implemented.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)