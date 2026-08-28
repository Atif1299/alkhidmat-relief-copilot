"""Auth API — login and me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.schemas import LoginRequest
from app.services.security import create_access_token, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    user_id: str


class MeResponse(BaseModel):
    id: str
    email: str
    role: str


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.active or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(subject=user.id, role=user.role, email=user.email)
    return TokenResponse(
        access_token=token,
        role=user.role,
        email=user.email,
        user_id=user.id,
    )


@router.get("/me", response_model=MeResponse)
def me(user: User | None = Depends(get_current_user)):
    # user is None only when AUTH_DISABLED=true (gates are open; UI needs a role).
    if user is None:
        return MeResponse(id="dev", email="auth-disabled@local", role="supervisor")
    return MeResponse(id=user.id, email=user.email, role=user.role)
