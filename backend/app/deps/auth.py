"""FastAPI auth dependencies — JWT role gates."""

from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import User
from app.db.session import get_db
from app.services.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> User | None:
    if settings.auth_disabled:
        return None
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(creds.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*roles: str) -> Callable:
    allowed = set(roles)

    def _dep(user: Annotated[User | None, Depends(get_current_user)]) -> User | None:
        if settings.auth_disabled:
            return None
        assert user is not None
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not allowed",
            )
        return user

    return _dep


# Common role bundles
RequireRequester = Annotated[User | None, Depends(require_roles("requester", "desk", "supervisor"))]
RequireDesk = Annotated[User | None, Depends(require_roles("desk", "supervisor"))]
RequireSupervisor = Annotated[User | None, Depends(require_roles("supervisor"))]
